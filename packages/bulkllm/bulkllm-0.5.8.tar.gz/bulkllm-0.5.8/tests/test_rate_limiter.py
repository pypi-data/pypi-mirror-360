import contextlib
import time

import anyio
import pytest

from bulkllm.rate_limiter import ModelRateLimit, RateLimiter


def test_has_capacity_exceeds_itpm():
    limit = ModelRateLimit(model_names=["m"], itpm=10)
    with pytest.raises(ValueError, match="input tokens per minute limit"):
        limit.has_capacity(15, 0)


def test_negative_tokens_rejected():
    limit = ModelRateLimit(model_names=["m"])
    with pytest.raises(ValueError, match="negative"):
        limit.has_capacity(-1, 0)


def test_reserve_record_usage_sync():
    limit = ModelRateLimit(model_names=["m"], rpm=2, tpm=50, itpm=50, otpm=50)
    with limit.reserve_capacity_sync(10, 5) as ctx:
        ctx.record_usage_sync(10, 5)
    assert limit.current_requests_in_window == 1
    assert not limit._pending_requests
    assert len(limit._completed_requests) == 1


def test_exit_without_record_raises():
    limit = ModelRateLimit(model_names=["m"], rpm=1)
    with pytest.raises(RuntimeError, match="Usage must be recorded"), limit.reserve_capacity_sync(1, 1):
        pass
    assert not limit._pending_requests
    assert limit.current_requests_in_window == 0


def test_exit_with_exception_propagates_and_cancels():
    limit = ModelRateLimit(model_names=["m"], rpm=1)
    with pytest.raises(ValueError, match="boom"), limit.reserve_capacity_sync(1, 1):
        raise ValueError("boom")
    assert not limit._pending_requests
    assert not limit._completed_requests


def test_get_rate_limit_for_model_with_regex():
    rl = RateLimiter([])
    pattern_limit = ModelRateLimit(model_names=["^foo-.*$"], rpm=5, is_regex=True)
    rl.add_rate_limit(pattern_limit)
    assert rl.get_rate_limit_for_model("foo-bar") is pattern_limit
    assert rl.get_rate_limit_for_model("other") is rl.default_rate_limit


@pytest.mark.asyncio
async def test_async_context_concurrent_usage():
    """Two workers should be able to hold separate contexts concurrently."""
    limit = ModelRateLimit(model_names=["m"], rpm=2)

    started1 = anyio.Event()
    started2 = anyio.Event()
    proceed = anyio.Event()

    async def worker(started: anyio.Event) -> None:
        # Each call to reserve_capacity should yield its own RateLimitContext.
        async with await limit.reserve_capacity(1, 1) as ctx:
            started.set()  # signal that we entered the context
            await proceed.wait()  # hold the context so both run together
            await ctx.record_usage(1, 1)

    async with anyio.create_task_group() as tg:
        tg.start_soon(worker, started1)
        tg.start_soon(worker, started2)

        # Wait until both workers have acquired capacity
        await started1.wait()
        await started2.wait()

        # At this point both contexts should be active simultaneously.
        assert len(limit._pending_requests) == 2

        proceed.set()

    # After all workers finish, the state should reflect two completed requests.
    assert not limit._pending_requests
    assert len(limit._completed_requests) == 2
    assert limit.current_requests_in_window == 2


@pytest.mark.asyncio
async def test_await_capacity_blocks_until_release() -> None:
    """``await_capacity`` should wait for other pending requests to release."""
    limit = ModelRateLimit(model_names=["m"], rpm=1)

    acquired = anyio.Event()
    release = anyio.Event()
    timings: dict[str, float] = {}

    async def holder() -> None:
        ctx = await limit.reserve_capacity(1, 1)
        acquired.set()
        await release.wait()

        exc_cls = anyio.get_cancelled_exc_class()
        with contextlib.suppress(exc_cls):
            await ctx.__aexit__(exc_cls, exc_cls(), None)

    async def waiter() -> None:
        await acquired.wait()
        start = time.monotonic()
        await limit.await_capacity(1, 1)
        timings["elapsed"] = time.monotonic() - start

    async with anyio.create_task_group() as tg:
        tg.start_soon(holder)
        tg.start_soon(waiter)

        await acquired.wait()
        await anyio.sleep(0.3)
        release.set()

    assert timings["elapsed"] >= 0.3
