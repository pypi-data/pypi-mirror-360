import time

import anyio
import pytest

from bulkllm.rate_limiter import ModelRateLimit, RateLimiter
from bulkllm.task_runner import LLMTask, LLMTaskRunner


async def _dummy_call(rl: RateLimiter, model: str, record: list[float]) -> None:
    async with await rl.reserve_capacity(model, 1, 1) as ctx:
        record.append(time.monotonic())
        await anyio.sleep(0.01)
        await ctx.record_usage(1, 1)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_runner_separate_queues(anyio_backend: str) -> None:
    rl = RateLimiter(
        [
            ModelRateLimit(model_names=["a"], rpm=1, window_seconds=1),
            ModelRateLimit(model_names=["b"], rpm=1, window_seconds=1),
        ]
    )
    runner = LLMTaskRunner(rate_limiter=rl, max_workers=2)
    starts_a: list[float] = []
    starts_b: list[float] = []

    tasks = [
        LLMTask("a", 1, 1, lambda: _dummy_call(rl, "a", starts_a)),
        LLMTask("b", 1, 1, lambda: _dummy_call(rl, "b", starts_b)),
        LLMTask("a", 1, 1, lambda: _dummy_call(rl, "a", starts_a)),
    ]
    runner.add_tasks(tasks)
    with anyio.fail_after(10):
        await runner.run()

    assert len(starts_a) == 2
    assert len(starts_b) == 1
    assert starts_b[0] < starts_a[1]
