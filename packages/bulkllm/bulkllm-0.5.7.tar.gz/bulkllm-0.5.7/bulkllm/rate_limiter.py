"""
Rate limiter for LLM APIs.

This module provides a mechanism for managing API rate limits for different LLM models:

- RateLimiter: Manages API rate limits for different LLM models by tracking
  requests per minute (rpm), tokens per minute (tpm), and output tokens per minute (otpm).

rate_limits = [
    # OpenAI GPT-4o family
    ModelRateLimit(
        model_names=[
            "openai/gpt-4o",
            "openai/gpt-4o-2024-05-13",
            "openai/gpt-4o-2024-08-06",
            "openai/gpt-4o-2024-11-20",
        ],
        rpm=50000,
        tpm=150000000,
    ),

]

limiter = RateLimiter()
estimated_input_tokens, estimated_output_tokens = 100, 200
async with limiter.reserve_capacity("openai/gpt-4o", estimated_input_tokens, estimated_output_tokens) as context:
    data, input_tokens, output_tokens = await my_task()
    await context.record_usage(input_tokens, output_tokens)


"""

import logging
import re
import threading
import time
import types
import uuid
from collections import deque
from dataclasses import dataclass
from re import Pattern

import anyio
from pydantic import BaseModel, Field, PrivateAttr

logger = logging.getLogger(__name__)


@dataclass
class Request:
    """Represents a single request tracked by the rate limiter."""

    id: str
    lock_acquisition_timestamp: float | None
    request_completion_timestamp: float | None
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        """Return combined input and output tokens."""
        return self.input_tokens + self.output_tokens


class RateLimitContext:
    """
    Context manager returned by :pymeth:`ModelRateLimit.reserve_capacity`
    (async) and :pymeth:`ModelRateLimit.reserve_capacity_sync` (sync).

    Call :pymeth:`record_usage` (async) **or** :pymeth:`record_usage_sync`
    right after the external API call completes so the limiter knows the real
    token usage.
    """

    def __init__(self, limiter: "ModelRateLimit", request_id: str):
        """Store the owning limiter and pending request id."""
        self._limiter = limiter
        self.request_id = request_id
        self._usage_recorded = False

    # ----------------------------- record usage ---------------------------- #
    async def record_usage(self, input_tokens: int, output_tokens: int, cached_hit: bool = False) -> None:
        """Async version."""
        if self._usage_recorded:
            logger.warning("Usage for request %s already recorded.", self.request_id)
            return

        await self._limiter.record_actual_usage(self.request_id, input_tokens, output_tokens, cached_hit=cached_hit)
        self._usage_recorded = True

    def record_usage_sync(self, input_tokens: int, output_tokens: int, cached_hit: bool = False) -> None:
        """Sync version."""
        if self._usage_recorded:
            logger.warning("Usage for request %s already recorded.", self.request_id)
            return

        self._limiter.record_actual_usage_sync(self.request_id, input_tokens, output_tokens, cached_hit=cached_hit)
        self._usage_recorded = True

    # ------------------------ async context methods ------------------------ #
    async def __aenter__(self):
        """Enter async context."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        """Exit async context, cancelling if necessary."""
        return await self._exit_async(exc_type, exc_val)

    # ------------------------- sync context methods ------------------------ #
    def __enter__(self):
        """Enter sync context."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        """Exit sync context, cancelling if needed."""
        return self._exit_sync(exc_type, exc_val)

    # ------------------------------ helpers -------------------------------- #
    def _exit_common(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        *,
        is_cancellation: bool,
    ) -> bool | None:
        """
        Synchronous helper that contains *all* logic shared by the async and
        sync exit paths.  It never blocks, so it can be called from either
        wrapper without `await`.
        """
        if self._usage_recorded:
            # Usage already persisted—nothing to clean up.
            return None

        log_level = logging.DEBUG if is_cancellation else logging.WARNING
        msg = f"Usage not recorded for request {self.request_id}. Cancelling pending request."
        if exc_type:
            msg += f" {'Cancellation' if is_cancellation else 'Exception'} occurred during context."
        logger.log(
            log_level,
            msg,
            exc_info=exc_val if exc_type and not is_cancellation else None,
        )

        # If there was *no* exception, exiting without usage is an error.
        if exc_type is None:
            msg = f"Usage must be recorded for request {self.request_id} on successful exit."
            raise RuntimeError(msg)

        # Propagate original exception / cancellation (return None).
        return None

    def _exit_sync(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
    ) -> bool | None:
        """
        Sync wrapper used by `__exit__`.
        Cancels the pending reservation synchronously, then delegates shared work.
        """
        # Cancel pending reservation
        self._limiter._cancel_pending_sync(self.request_id)
        return self._exit_common(
            exc_type,
            exc_val,
            is_cancellation=False,  # cancellation doesn`t exist in sync path
        )

    async def _exit_async(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
    ) -> bool | None:
        """
        Async wrapper used by `__aexit__`.
        Cancels the pending reservation asynchronously, then delegates shared work.
        """
        is_cancellation = exc_type is not None and issubclass(exc_type, anyio.get_cancelled_exc_class())
        # Cancel pending reservation
        await self._limiter._cancel_pending(self.request_id)
        return self._exit_common(exc_type, exc_val, is_cancellation=is_cancellation)


class ModelRateLimit(BaseModel):
    """Manages rate limits for a specific model or group of models."""

    model_names: list[str] = Field(..., description="Models that share this rate limit")
    rpm: int = Field(0, description="Requests per minute")
    tpm: int = Field(0, description="Total tokens per minute")
    itpm: int = Field(0, description="Input tokens per minute")
    otpm: int = Field(0, description="Output tokens per minute")
    is_regex: bool = Field(False, description="If *model_names* are regex patterns")
    window_seconds: int = Field(60, description="Window size in seconds")
    pending_timeout_seconds: int = Field(120, description="Pending request timeout in seconds")

    # Locks
    _lock: anyio.Lock = PrivateAttr(default_factory=anyio.Lock)
    _thread_lock: threading.RLock = PrivateAttr(default_factory=threading.RLock)

    # Requests
    _pending_requests: dict[str, Request] = PrivateAttr(default_factory=dict)
    _completed_requests: deque[Request] = PrivateAttr(default_factory=deque)

    # Running totals
    _pending_input_tokens: int = PrivateAttr(0)
    _pending_output_tokens: int = PrivateAttr(0)
    _completed_input_tokens: int = PrivateAttr(0)
    _completed_output_tokens: int = PrivateAttr(0)

    # --------------------------- convenience props ------------------------- #
    @property
    def current_requests_in_window(self) -> int:
        """Return number of requests currently counted in the window."""
        return len(self._pending_requests) + len(self._completed_requests)

    @property
    def remaining_requests_per_minute(self) -> float | int:
        """Requests remaining before hitting the RPM limit."""
        return float("inf") if self.rpm <= 0 else max(0, self.rpm - self.current_requests_in_window)

    @property
    def current_total_tokens_in_window(self) -> int:
        """
        Returns the total number of tokens (input + output) currently counted
        against the TPM limit (pending + completed within the window).
        Note: Accessing this property does not acquire the lock, values are read atomically
        but the combined sum represents a potentially slightly stale snapshot.
        Call _cleanup_old_requests within a lock context before accessing if needed.
        """
        return (
            self._pending_input_tokens
            + self._pending_output_tokens
            + self._completed_input_tokens
            + self._completed_output_tokens
        )

    @property
    def remaining_total_tokens_per_minute(self) -> float | int:
        """Tokens remaining before hitting the TPM limit."""
        return float("inf") if self.tpm <= 0 else max(0, self.tpm - self.current_total_tokens_in_window)

    @property
    def current_input_tokens_in_window(self) -> int:
        """Return input tokens counted in the current window."""
        return self._pending_input_tokens + self._completed_input_tokens

    @property
    def remaining_input_tokens_per_minute(self) -> float | int:
        """Input tokens remaining before hitting the ITPM limit."""
        return float("inf") if self.itpm <= 0 else max(0, self.itpm - self.current_input_tokens_in_window)

    @property
    def current_output_tokens_in_window(self) -> int:
        """Return output tokens counted in the current window."""
        return self._pending_output_tokens + self._completed_output_tokens

    @property
    def remaining_output_tokens_per_minute(self) -> float | int:
        """Output tokens remaining before hitting the OTPM limit."""
        return float("inf") if self.otpm <= 0 else max(0, self.otpm - self.current_output_tokens_in_window)

    # ----------------------------- diagnostics ----------------------------- #
    def print_current_status(self) -> None:
        """Print the current rate-limit utilisation."""
        print(f"Current window: {self.window_seconds}s")
        if self.rpm:
            print(f"Requests: {self.current_requests_in_window} / {self.rpm}")
        if self.tpm:
            print(f"Tokens: {self.current_total_tokens_in_window} / {self.tpm}")
        if self.itpm:
            print(f"Input tokens: {self.current_input_tokens_in_window} / {self.itpm}")
        if self.otpm:
            print(f"Output tokens: {self.current_output_tokens_in_window} / {self.otpm}")

    # ---------------------------- housekeeping ----------------------------- #
    def _cleanup_old_requests(self) -> None:
        """Remove completed/pending requests that aged out of the sliding window."""
        cutoff_time = time.monotonic() - self.window_seconds

        while self._completed_requests and self._completed_requests[0].request_completion_timestamp < cutoff_time:
            expired = self._completed_requests.popleft()
            self._completed_input_tokens -= expired.input_tokens
            self._completed_output_tokens -= expired.output_tokens
            self._completed_input_tokens = max(0, self._completed_input_tokens)
            self._completed_output_tokens = max(0, self._completed_output_tokens)

        # Prune stalled pending requests
        cutoff_time = time.monotonic() - self.pending_timeout_seconds
        for request_id, req in list(self._pending_requests.items()):
            if req.lock_acquisition_timestamp < cutoff_time:
                logger.warning(
                    "Pending request %s timed out after %ss. Removing from tracking.",
                    request_id,
                    self.pending_timeout_seconds,
                )
                self._pending_input_tokens -= req.input_tokens
                self._pending_output_tokens -= req.output_tokens
                self._pending_input_tokens = max(0, self._pending_input_tokens)
                self._pending_output_tokens = max(0, self._pending_output_tokens)
                del self._pending_requests[request_id]

    # ------------------------ capacity / eligibility ----------------------- #
    def _can_make_request(self, desired_input_tokens: int, desired_output_tokens: int) -> bool:
        """Check if making a new request would violate any rate limits."""
        self._cleanup_old_requests()
        return self.has_capacity(desired_input_tokens, desired_output_tokens)

    def has_capacity(self, desired_input_tokens: int, desired_output_tokens: int) -> bool:
        """Return True if the request would not exceed any limits."""
        logger.debug(
            f"Checking if can make request for {self.model_names} with estimated tokens: {desired_input_tokens}, {desired_output_tokens}"
        )

        if desired_input_tokens < 0 or desired_output_tokens < 0:
            raise ValueError("negative token counts are not allowed")

        if self.rpm and self.current_requests_in_window + 1 > self.rpm:
            logger.debug(f"Request count {self.current_requests_in_window} + 1 > rpm {self.rpm}, returning False")
            return False

        if self.itpm:
            if desired_input_tokens > self.itpm:
                msg = f"Estimated input tokens ({desired_input_tokens}) exceed the input tokens per minute limit ({self.itpm}). Request can never be fulfilled."
                raise ValueError(msg)

            if self.current_input_tokens_in_window + desired_input_tokens > self.itpm:
                logger.debug(
                    f"Current input tokens {self.current_input_tokens_in_window} + estimated input tokens {desired_input_tokens} > itpm {self.itpm}, returning False"
                )
                return False

        if self.otpm:
            if desired_output_tokens > self.otpm:
                msg = f"Estimated output tokens ({desired_output_tokens}) exceed the output tokens per minute limit ({self.otpm}). Request can never be fulfilled."
                raise ValueError(msg)

            if self.current_output_tokens_in_window + desired_output_tokens > self.otpm:
                logger.debug(
                    f"Current output tokens {self.current_output_tokens_in_window} + estimated output tokens {desired_output_tokens} > otpm {self.otpm}, returning False"
                )
                return False

        if self.tpm:
            total_tokens = self.current_input_tokens_in_window + self.current_output_tokens_in_window
            estimated_total_tokens = desired_input_tokens + desired_output_tokens

            if estimated_total_tokens > self.tpm:
                msg = f"Estimated total tokens ({estimated_total_tokens}) exceed the total tokens per minute limit ({self.tpm}). Request can never be fulfilled."
                raise ValueError(msg)

            if total_tokens + estimated_total_tokens > self.tpm:
                logger.debug(
                    f"Total tokens {total_tokens} + estimated input tokens {desired_input_tokens} + estimated output tokens {desired_output_tokens} > tpm {self.tpm}, returning False"
                )
                return False

        return True

    # ---------------------------- wait helpers ---------------------------- #
    def await_capacity_sync(self, input_tokens: int, output_tokens: int) -> None:
        """Block until capacity is available for the desired tokens."""
        while True:
            with self._thread_lock:
                self._cleanup_old_requests()
                if self.has_capacity(input_tokens, output_tokens):
                    return
            time.sleep(0.05)

    async def await_capacity(self, input_tokens: int, output_tokens: int) -> None:
        """Async version of :meth:`await_capacity_sync`."""
        while True:
            async with self._lock:
                self._cleanup_old_requests()
                if self.has_capacity(input_tokens, output_tokens):
                    return
            await anyio.sleep(0.05)

    # ---------------------------- acquire logic ---------------------------- #
    # Internal helper (no locking)
    def _try_acquire(self, in_tok: int, out_tok: int) -> str | None:
        """Attempt to reserve capacity—caller must already hold *some* lock."""
        if not self._can_make_request(in_tok, out_tok):
            return None

        now = time.monotonic()
        req_id = str(uuid.uuid4())
        req = Request(
            id=req_id,
            lock_acquisition_timestamp=now,
            request_completion_timestamp=None,
            input_tokens=in_tok,
            output_tokens=out_tok,
        )
        self._pending_requests[req_id] = req
        self._pending_input_tokens += in_tok
        self._pending_output_tokens += out_tok
        return req_id

    # ---------- async variants ---------- #
    async def acquire(self, in_tok: int, out_tok: int) -> str | None:
        """Attempt to acquire capacity asynchronously."""
        async with self._lock:
            return self._try_acquire(in_tok, out_tok)

    async def acquire_blocking(self, in_tok: int, out_tok: int) -> str:
        """Keep trying :meth:`acquire` until successful."""
        while True:
            req_id = await self.acquire(in_tok, out_tok)
            if req_id:
                return req_id
            await anyio.sleep(0.1)

    async def reserve_capacity(self, est_in: int, est_out: int) -> RateLimitContext:
        """Acquire capacity and return a context manager."""
        req_id = await self.acquire_blocking(est_in, est_out)
        return RateLimitContext(self, req_id)

    # ---------- sync variants ----------- #
    def acquire_sync(self, in_tok: int, out_tok: int) -> str | None:
        """Attempt to acquire capacity synchronously."""
        with self._thread_lock:
            return self._try_acquire(in_tok, out_tok)

    def acquire_blocking_sync(self, in_tok: int, out_tok: int) -> str:
        """Blocking version of :meth:`acquire_sync`."""
        while True:
            req_id = self.acquire_sync(in_tok, out_tok)
            if req_id:
                return req_id
            time.sleep(0.1)

    def reserve_capacity_sync(self, est_in: int, est_out: int) -> RateLimitContext:
        """Blocking wrapper returning a :class:`RateLimitContext`."""
        req_id = self.acquire_blocking_sync(est_in, est_out)
        return RateLimitContext(self, req_id)

    # ----------------------- record / cancel helpers ----------------------- #
    # Internal implementation shared by sync & async
    def _record_actual_usage_internal(self, request_id: str, in_tok: int, out_tok: int, cached_hit: bool) -> None:
        """Update token counts once the request finishes."""
        if request_id in self._pending_requests:
            req = self._pending_requests.pop(request_id)
            self._pending_input_tokens -= req.input_tokens
            self._pending_output_tokens -= req.output_tokens
            self._pending_input_tokens = max(0, self._pending_input_tokens)
            self._pending_output_tokens = max(0, self._pending_output_tokens)
        else:
            logger.warning("Request ID %s not in pending when recording usage.", request_id)
            req = Request(
                id=request_id,
                lock_acquisition_timestamp=None,
                request_completion_timestamp=time.monotonic(),
                input_tokens=in_tok,
                output_tokens=out_tok,
            )

        if not cached_hit:
            req.input_tokens = in_tok
            req.output_tokens = out_tok
            req.request_completion_timestamp = time.monotonic()

            self._completed_requests.append(req)
            self._completed_input_tokens += in_tok
            self._completed_output_tokens += out_tok

        self._cleanup_old_requests()

    # ---------- async record ---------- #
    async def record_actual_usage(
        self, request_id: str, input_tokens: int, output_tokens: int, cached_hit: bool = False
    ) -> None:
        """Record actual usage asynchronously."""
        async with self._lock:
            self._record_actual_usage_internal(request_id, input_tokens, output_tokens, cached_hit)

    # ---------- sync record ----------- #
    def record_actual_usage_sync(
        self, request_id: str, input_tokens: int, output_tokens: int, cached_hit: bool = False
    ) -> None:
        """Record actual usage synchronously."""
        with self._thread_lock:
            self._record_actual_usage_internal(request_id, input_tokens, output_tokens, cached_hit)

    # ------------------------ cancel helpers (shared) ---------------------- #
    def _cancel_pending_internal(self, request_id: str) -> None:
        """Remove a pending request without recording usage."""
        if request_id in self._pending_requests:
            req = self._pending_requests.pop(request_id)
            self._pending_input_tokens -= req.input_tokens
            self._pending_output_tokens -= req.output_tokens
            self._pending_input_tokens = max(0, self._pending_input_tokens)
            self._pending_output_tokens = max(0, self._pending_output_tokens)
            logger.info("Cancelled pending request %s.", request_id)

    async def _cancel_pending(self, request_id: str) -> None:
        """Async wrapper around :meth:`_cancel_pending_internal`."""

        if request_id in self._pending_requests:
            async with self._lock:
                self._cancel_pending_internal(request_id)

    def _cancel_pending_sync(self, request_id: str) -> None:
        """Sync wrapper around :meth:`_cancel_pending_internal`."""
        with self._thread_lock:
            self._cancel_pending_internal(request_id)


class RateLimiter:
    """Manages rate limits for all models, routing to the appropriate ModelRateLimit."""

    def __init__(self, rate_limits: list[ModelRateLimit] | None = None):
        """Initialise lookup tables and load default rate limits."""
        self.model_limit_lookup: dict[str, ModelRateLimit] = {}

        # Store regex patterns for model matching
        self.regex_patterns: list[tuple[Pattern, ModelRateLimit]] = []

        # Default rate limits
        self.default_rate_limit = ModelRateLimit(model_names=["default"], rpm=0, tpm=0, itpm=0, otpm=0)
        # Use passed limits if provided, otherwise use defaults. Handles None and empty list correctly.

        if rate_limits is None:
            from .rate_limits import DEFAULT_RATE_LIMITS

            rate_limits = DEFAULT_RATE_LIMITS

        for rate_limit in rate_limits:
            self.add_rate_limit(rate_limit)

    def add_rate_limit(self, rate_limit: ModelRateLimit):
        """Register a :class:`ModelRateLimit` with this limiter."""
        if not rate_limit or not rate_limit.model_names:
            return

        # Handle regex patterns
        if rate_limit.is_regex:
            for pattern_str in rate_limit.model_names:
                pattern = re.compile(pattern_str)
                self.regex_patterns.append((pattern, rate_limit))
        else:
            for model_name in rate_limit.model_names:
                self.model_limit_lookup[model_name] = rate_limit

    def get_rate_limit_for_model(self, model_name: str) -> ModelRateLimit:
        """Get the ModelRateLimit instance for a model."""
        model_limit = self.model_limit_lookup.get(model_name)
        if model_limit:
            return model_limit

        for pattern, model_limit in self.regex_patterns:
            if pattern.match(model_name):
                return model_limit

        return self.default_rate_limit

    async def reserve_capacity(self, model_name: str, input_tokens: int, output_tokens: int) -> RateLimitContext:
        """Reserve capacity for a request. Returns RateLimitContext if successful, None otherwise."""
        rate_limit = self.get_rate_limit_for_model(model_name)
        return await rate_limit.reserve_capacity(input_tokens, output_tokens)

    def reserve_capacity_sync(self, model_name: str, input_tokens: int, output_tokens: int) -> RateLimitContext:
        """Blocking wrapper around :pymeth:`ModelRateLimit.reserve_capacity`."""
        rate_limit = self.get_rate_limit_for_model(model_name)
        return rate_limit.reserve_capacity_sync(input_tokens, output_tokens)

    def has_capacity(self, model_name: str, desired_input_tokens: int, desired_output_tokens: int) -> bool:
        """Check capacity for a particular model."""
        rate_limit = self.get_rate_limit_for_model(model_name)
        return rate_limit.has_capacity(desired_input_tokens, desired_output_tokens)

    def await_capacity_sync(self, model_name: str, input_tokens: int, output_tokens: int) -> None:
        """Block until the specified model has room for a new request."""
        rate_limit = self.get_rate_limit_for_model(model_name)
        rate_limit.await_capacity_sync(input_tokens, output_tokens)

    async def await_capacity(self, model_name: str, input_tokens: int, output_tokens: int) -> None:
        """Async version of :meth:`await_capacity_sync`."""
        rate_limit = self.get_rate_limit_for_model(model_name)
        await rate_limit.await_capacity(input_tokens, output_tokens)
