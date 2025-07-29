from bulkllm.rate_limiter import ModelRateLimit
from bulkllm.rate_limits import DEFAULT_RATE_LIMITS


def test_default_rate_limits_non_empty() -> None:
    assert DEFAULT_RATE_LIMITS


def test_default_rate_limits_types_and_models() -> None:
    assert all(isinstance(rl, ModelRateLimit) for rl in DEFAULT_RATE_LIMITS)
    model_names = [name for rl in DEFAULT_RATE_LIMITS for name in rl.model_names]
    assert "openai/gpt-4o" in model_names
