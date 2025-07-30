import asyncio
from typing import Any
from revoltlogger import Logger,LogLevel


class AsyncQueue:
    def __init__(self, maxsize: int = 0, debug: bool = False):
        self._queue = asyncio.Queue(maxsize=maxsize)
        self._debug = debug
        self.logger = Logger(name="",level=LogLevel.DEBUG)

    async def put(self, item: Any) -> None:
        await self._queue.put(item)
        if self._debug:
            self.logger.debug(f"Item added to queue: {item!r}")

    async def get(self) -> Any:
        item = await self._queue.get()
        if self._debug:
            self.logger.debug(f"Item retrieved from queue: {item!r}")
        return item

    def task_done(self) -> None:
        self._queue.task_done()
        if self._debug:
            self.logger.debug("Marked a task as done")

    async def join(self) -> None:
        if self._debug:
            self.logger.debug("Waiting for all tasks in queue to complete")
        await self._queue.join()
        if self._debug:
            self.logger.debug("All tasks completed")

    def qsize(self) -> int:
        size = self._queue.qsize()
        if self._debug:
            self.logger.debug(f"Current queue size: {size}")
        return size

    def empty(self) -> bool:
        is_empty = self._queue.empty()
        if self._debug:
            self.logger.debug(f"Is queue empty? {is_empty}")
        return is_empty

    def full(self) -> bool:
        is_full = self._queue.full()
        if self._debug:
            self.logger.debug(f"Is queue full? {is_full}")
        return is_full

    def maxsize(self) -> int:
        size = self._queue.maxsize
        if self._debug:
            self.logger.debug(f"Queue maxsize: {size}")
        return size
