import time
import collections
import heapq
from typing import Any, Coroutine, Union


class Awaitable:
    def __await__(self):
        yield


class Scheduler:
    def __init__(self):
        self._tasks_ready = collections.deque()
        self._sleeping = []
        self._current = None
        self._sequence = 0

    def get_current_task(self) -> Coroutine[Any, Any, Any]:
        return self._current

    def set_no_current(self) -> None:
        self._current = None

    @staticmethod
    def switch() -> Awaitable:
        return Awaitable()

    async def sleep(self, delay: Union[int, float]) -> None:
        deadline = time.time() + delay
        heapq.heappush(
            self._sleeping,
            (deadline, self._sequence, self._current)
        )
        self._sequence += 1
        self._current = None
        await self.switch()

    def add_task(self, coro: Coroutine[Any, Any, Any]) -> None:
        self._tasks_ready.append(coro)

    def run(self) -> None:
        while self._tasks_ready or self._sleeping:

            if not self._tasks_ready:
                deadline, _, coro = heapq.heappop(self._sleeping)
                time_to_wait = deadline - time.time()
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                self._tasks_ready.append(coro)

            self._current = self._tasks_ready.popleft()
            try:
                self._current.send(None)
                if self._current:
                    self._tasks_ready.append(self._current)
            except StopIteration:
                pass


class QueueClosed(Exception):
    pass


class AsyncQueue:

    def __init__(self, schler: Scheduler):
        self._scheduler = schler
        self._items = collections.deque()
        self._waiting = collections.deque()
        self._closed = False

    def close(self) -> None:
        self._closed = True
        if self._waiting and not self._items:
            still_waiting_coro = self._waiting.popleft()
            self._scheduler.add_task(still_waiting_coro)

    async def put(self, item):
        if self._closed:
            raise QueueClosed()

        self._items.append(item)
        if self._waiting:
            first_waiting_task = self._waiting.popleft()
            self._scheduler.add_task(first_waiting_task)

    async def get(self):
        while not self._items:
            if self._closed:
                raise QueueClosed()
            self._waiting.append(self._scheduler.get_current_task())
            self._scheduler.set_no_current()
            await self._scheduler.switch()
        return self._items.popleft()


async def producer(sched: Scheduler, q: AsyncQueue, amount: int) -> None:
    for i in range(amount):
        print(f'Produced {i}')
        await q.put(i)
        await sched.sleep(.5)

    print(f'Producer done. Queue is getting closed.')
    q.close()


async def consumer(q: AsyncQueue) -> None:
    try:
        while True:
            item = await q.get()
            print(f'Consumed {item}')
    except QueueClosed:
        print(f'QueueClosed exception caught. Consumer done.')


if __name__ == '__main__':
    sched = Scheduler()
    q = AsyncQueue(sched)
    sched.add_task(
        producer(sched, q, 10)
    )
    sched.add_task(
        consumer(q)
    )
    sched.run()
