import functools
import inspect
import logging
import time
from asyncio import CancelledError
from pathlib import Path

import litellm
import litellm.exceptions
import tenacity
from litellm.cost_calculator import completion_cost

from bulkllm.rate_limiter import RateLimiter
from bulkllm.usage_tracker import convert_litellm_usage_to_usage_record, track_usage

logger = logging.getLogger(__name__)


CACHE_PATH = Path(__file__).parent.parent.parent / ".litellm_cache"


def patch_LLMCachingHandler():
    """this is a workaround to let us detect which responses came from cache"""
    from litellm.caching.caching_handler import LLMCachingHandler

    if not hasattr(LLMCachingHandler._convert_cached_result_to_model_response, "is_patched"):
        original_method = LLMCachingHandler._convert_cached_result_to_model_response

        def wrapped_method(self, *args, **kwargs):
            result = original_method(self, *args, **kwargs)
            if isinstance(result, litellm.ModelResponse):
                result.is_cached_hit = True  # type: ignore
            return result

        wrapped_method.is_patched = True  # type: ignore
        LLMCachingHandler._convert_cached_result_to_model_response = wrapped_method  # type: ignore


_SCRUB_ALLOW_ATTRS = {
    "metadata.user_api_key_hash",
    "metadata.user_api_key_alias",
    "metadata.user_api_key_team_id",
    "metadata.user_api_key_org_id",
    "metadata.user_api_key_user_id",
    "metadata.user_api_key_team_alias",
    "metadata.user_api_key_user_email",
    "metadata.user_api_key_end_user_id",
}

_SCRUB_ALLOW_PREFIXES = ("LLM_COMPLETIONS", "LLM_PROMPTS")


def _scrubbing_callback(m):
    if len(m.path) == 2 and m.path[0] == "attributes" and m.path[1] in _SCRUB_ALLOW_ATTRS:
        """Allow certain metadata fields to bypass log scrubbing."""
        return m.value

    if len(m.path) > 1 and any(prefix in m.path[1] for prefix in _SCRUB_ALLOW_PREFIXES):
        return m.value


@functools.lru_cache
def initialize_litellm(enable_logfire=False):
    """Initialise LiteLLM and optional Logfire instrumentation."""
    patch_LLMCachingHandler()
    if enable_logfire:
        import logfire  # type: ignore

        logfire.configure(
            token="",
            console=False,
            scrubbing=logfire.ScrubbingOptions(callback=_scrubbing_callback),
        )

        # litellm.success_callback = ["logfire"]
        # litellm.failure_callback = ["logfire"]
        litellm.callbacks = ["logfire"]

    disk_cache_dir = CACHE_PATH
    litellm.cache = litellm.Cache(type="disk", disk_cache_dir=disk_cache_dir)  # type: ignore
    litellm.enable_cache()
    litellm.suppress_debug_info = True


# Add global rat
@functools.cache
def rate_limiter() -> RateLimiter:
    """Return a singleton RateLimiter shared across the process."""
    return RateLimiter()


def _estimate_tokens(bound_args):
    """Estimate input and output token counts from bound args."""
    model_name = bound_args.get("model")
    if model_name is None:
        msg = "Model name must be supplied as first positional arg or 'model' kwarg."
        raise ValueError(msg)

    messages = bound_args.get("messages")
    if isinstance(messages, str):
        input_tokens = litellm.token_counter(model=model_name, text=messages)
    else:
        input_tokens = litellm.token_counter(model=model_name, messages=messages)

    max_completion = bound_args.get("max_completion_tokens") or bound_args.get("max_tokens") or 1
    output_tokens = max_completion
    return input_tokens, output_tokens, model_name


@functools.wraps(litellm.acompletion)
async def acompletion(*args, retry_cfg: dict | None = None, **kwargs):
    """
    Drop-in replacement for litellm.acompletion with dynamic Tenacity retries.

    Parameters
    ----------
    retry_cfg : dict | None
        Tenacity config (stop, wait, retry …).  Uses _DEFAULT_RETRY_CFG if None.
    """
    retry_cfg = retry_cfg or _DEFAULT_RETRY_CFG
    retrying = tenacity.AsyncRetrying(**retry_cfg)

    async for attempt in retrying:
        with attempt:
            return await _acompletion(*args, **kwargs)


@functools.wraps(litellm.acompletion)
async def _acompletion(*args, **kwargs):
    """Asynchronous wrapper with rate limiting via global RateLimiter."""
    initialize_litellm()
    bound_args = inspect.signature(litellm.completion).bind_partial(*args, **kwargs).arguments
    input_tokens, output_tokens, model_name = _estimate_tokens(bound_args)
    # kwargs["cache"] = {"no-cache": True}

    async with await rate_limiter().reserve_capacity(model_name, input_tokens, output_tokens) as ctx:
        start_ms = time.monotonic()

        response = await litellm.acompletion(*args, **kwargs)

        duration_ms = (time.monotonic() - start_ms) * 1000

        usage = getattr(response, "usage", {}) or {}
        cached_hit = getattr(response, "is_cached_hit", False)
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        await ctx.record_usage(
            prompt_tokens,
            completion_tokens,
            cached_hit=cached_hit,
        )
    cost_usd = getattr(response, "_hidden_params", {}).get("response_cost", None)
    if cost_usd is None:
        response.model = model_name
        try:
            cost_usd = completion_cost(completion_response=response)
        except Exception:  # noqa - best effort for mocks
            cost_usd = 0.0

    usage_record = convert_litellm_usage_to_usage_record(
        litellm_usage=usage,
        model=model_name,
        time_ms=duration_ms,
        cost_usd=cost_usd,
        is_cached_hit=cached_hit,
    )

    track_usage(
        model=model_name,
        record=usage_record,
    )

    response.is_cached_hit = cached_hit
    response.standardized_usage = usage_record
    return response


@functools.wraps(litellm.completion)
def _completion(*args, **kwargs):
    """Synchronous wrapper with rate limiting via global RateLimiter."""
    initialize_litellm()
    bound = inspect.signature(litellm.completion).bind_partial(*args, **kwargs)
    input_tokens, output_tokens, model_name = _estimate_tokens(bound.arguments)

    with rate_limiter().reserve_capacity_sync(model_name, input_tokens, output_tokens) as ctx:
        start_ms = time.monotonic()
        try:
            response = litellm.completion(*args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to complete request for model '{model_name}': {e}")
            raise

        duration_ms = (time.monotonic() - start_ms) * 1000

        usage = getattr(response, "usage", {}) or {}
        cached_hit = getattr(response, "is_cached_hit", False)
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        ctx.record_usage_sync(
            prompt_tokens,
            completion_tokens,
            cached_hit=cached_hit,
        )
    cost_usd = getattr(response, "_hidden_params", {}).get("response_cost", None)
    if cost_usd is None:
        response.model = model_name
        try:
            cost_usd = completion_cost(completion_response=response)
        except Exception:  # noqa - best effort for mocks
            cost_usd = 0.0
    usage_record = convert_litellm_usage_to_usage_record(
        litellm_usage=usage,
        model=model_name,
        time_ms=duration_ms,
        cost_usd=cost_usd,
        is_cached_hit=cached_hit,
    )

    track_usage(
        model=model_name,
        record=usage_record,
    )

    response.is_cached_hit = getattr(response, "is_cached_hit", False)
    return response


@functools.wraps(litellm.completion)
def completion(*args, retry_cfg: dict | None = None, **kwargs):
    """Synchronous wrapper with rate limiting via global RateLimiter."""
    retry_cfg = retry_cfg or _DEFAULT_RETRY_CFG
    retrying = tenacity.Retrying(**retry_cfg)

    for attempt in retrying:
        with attempt:
            return _completion(*args, **kwargs)


def should_retry_error(exception):
    """Determine if an error from litellm.acompletion should be retried."""
    if "model_not_found" in str(exception) or "does not exist" in str(exception):
        return False
    if "authentication" in str(exception).lower() or "auth" in str(exception).lower():
        return False
    if "permission" in str(exception).lower() or "access" in str(exception).lower():
        return False
    if isinstance(exception, litellm.exceptions.BadRequestError):
        return False
    if isinstance(
        exception,
        litellm.exceptions.APIConnectionError
        | litellm.exceptions.Timeout
        | litellm.exceptions.RateLimitError
        | litellm.exceptions.ServiceUnavailableError,
    ):
        logger.warning(f"Retrying API call due to {type(exception).__name__}: {exception}")
        return True
    if isinstance(exception, CancelledError):
        return False
    logger.error(f"Non-retryable error encountered: {type(exception).__name__}", exc_info=False)
    return False


_DEFAULT_RETRY_CFG = {
    "stop": tenacity.stop_after_attempt(3),
    "wait": tenacity.wait_exponential(multiplier=1, min=1, max=10),
    "retry": tenacity.retry_if_exception(should_retry_error),
    "reraise": True,
}
