import time

import anyio

from bulkllm.rate_limiter import ModelRateLimit


async def _benchmark(concurrency: int, duration: float) -> dict[str, float]:
    limit = ModelRateLimit(model_names=["m"])  # no limits
    start = time.monotonic()
    stop = start + duration
    stats = {"count": 0, "max_pending": 0}

    async def worker() -> None:
        nonlocal stats
        local_count = 0
        local_max = 0
        while time.monotonic() < stop:
            ctx = await limit.reserve_capacity(1, 1)
            async with ctx:
                current = len(limit._pending_requests)
                local_max = max(local_max, current)
                await anyio.sleep(0.005)
                await ctx.record_usage(1, 1)
                local_count += 1
        stats["count"] += local_count
        stats["max_pending"] = max(stats["max_pending"], local_max)

    async with anyio.create_task_group() as tg:
        for _ in range(concurrency):
            tg.start_soon(worker)

    stats["duration"] = time.monotonic() - start
    return stats


def test_rate_limiter_performance() -> None:
    duration = 10.0
    concurrency = 50
    stats = anyio.run(_benchmark, concurrency, duration)
    rps = stats["count"] / stats["duration"]
    print(
        f"Completed {stats['count']} tasks in {stats['duration']:.2f}s "
        f"with peak pending {stats['max_pending']} using {concurrency} workers."
    )
    print(f"Throughput: {rps:.2f} tasks/sec")
