import time
import collections
import heapq
from typing import Any, Coroutine, Union


class Scheduler:
    def __init__(self):
        self._tasks_ready = collections.deque()
        self._sleeping = []
        self._current = None
        self._sequence = 0

    async def sleep(self, delay: Union[int, float]) -> None:
        deadline = time.time() + delay
        heapq.heappush(
            self._sleeping,
            (deadline, self._sequence, self._current)
        )
        self._sequence += 1
        self._current = None
        await switch()

    def add_task(self, coro: Coroutine[Any, Any, Any]):
        self._tasks_ready.append(coro)

    def run(self):
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


class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()


async def count_down(sched: Scheduler, start: int) -> None:
    while start > 0:
        print(start)
        await sched.sleep(4)
        start -= 1
    print(start)
    print('Countdown finished')


async def count_up(sched: Scheduler, stop: int, start: int = 0) -> None:
    while stop > start:
        print(start)
        await sched.sleep(1)
        start += 1
    print(start)
    print('Count up finished')


if __name__ == '__main__':
    sched = Scheduler()
    sched.add_task(count_down(sched, 5))
    sched.add_task(count_up(sched, 20))
    sched.run()
