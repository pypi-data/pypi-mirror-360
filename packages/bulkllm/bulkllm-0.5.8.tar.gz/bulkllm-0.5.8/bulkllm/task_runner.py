from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .rate_limiter import RateLimiter

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


@dataclass(slots=True)
class LLMTask:
    """Represents a single LLM call to be executed."""

    model_name: str
    estimate_in: int
    estimate_out: int
    fn: Callable[[], Awaitable[Any]]


class LLMTaskRunner:
    """Simple scheduler that runs tasks with per-model queues."""

    def __init__(self, rate_limiter: RateLimiter | None = None, *, max_workers: int = 4) -> None:
        self._queues: dict[str, asyncio.Queue[LLMTask]] = defaultdict(asyncio.Queue)
        self._sem = asyncio.Semaphore(max_workers)
        self._rate_limiter = rate_limiter or RateLimiter()
        self._max_workers = max_workers

    def add_tasks(self, tasks: list[LLMTask]) -> None:
        """Add a batch of tasks to their model-specific queues."""
        for task in tasks:
            self._queues[task.model_name].put_nowait(task)

    async def _model_worker(self, model_name: str) -> None:
        queue = self._queues[model_name]
        while True:
            task = await queue.get()
            await self._rate_limiter.await_capacity(
                model_name=task.model_name,
                input_tokens=task.estimate_in,
                output_tokens=task.estimate_out,
            )
            async with self._sem:
                try:
                    await task.fn()
                finally:
                    queue.task_done()
            if queue.empty():
                break

    async def run(self) -> None:
        """Run tasks for all known models and wait for completion."""
        async with asyncio.TaskGroup() as tg:
            for model in list(self._queues):
                tg.create_task(self._model_worker(model))
