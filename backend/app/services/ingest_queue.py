import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


TelemetryDict = dict[str, Any]


class TelemetryIngestQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[TelemetryDict] = asyncio.Queue(maxsize=10_000)

    async def put(self, item: TelemetryDict) -> None:
        await self._queue.put(item)

    def put_threadsafe(self, loop: asyncio.AbstractEventLoop, item: TelemetryDict) -> None:
        loop.call_soon_threadsafe(self._queue.put_nowait, item)

    async def run_consumer(self, handler: Callable[[TelemetryDict], Awaitable[None]]) -> None:
        while True:
            item = await self._queue.get()
            try:
                await handler(item)
            finally:
                self._queue.task_done()


telemetry_queue = TelemetryIngestQueue()

