import concurrent.futures

from bulkllm.rate_limiter import ModelRateLimit


def _reserve_and_record(limit: ModelRateLimit) -> None:
    """Reserve capacity in the limiter and immediately record the usage."""
    # This helper runs in multiple threads simultaneously. Each invocation
    # should succeed in reserving and recording exactly one request worth of
    # capacity if the limiter's internal locking is correct.
    with limit.reserve_capacity_sync(1, 1) as ctx:
        ctx.record_usage_sync(1, 1)


def test_rate_limiter_thread_safe():
    """Ensure ModelRateLimit behaves correctly when used from multiple threads."""
    limit = ModelRateLimit(model_names=["m"], rpm=1000, itpm=1000, otpm=1000)

    # Launch several threads that all reserve capacity and record usage
    # concurrently. If the limiter isn't thread-safe, race conditions would
    # leave `_pending_requests` non-empty or the totals inconsistent.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(lambda _: _reserve_and_record(limit), range(50)))

    assert limit.current_requests_in_window == 50
    assert not limit._pending_requests
    assert len(limit._completed_requests) == 50
    assert limit._completed_input_tokens == 50
    assert limit._completed_output_tokens == 50
