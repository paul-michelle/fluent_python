import collections
import time
import heapq
from typing import Callable, Any, Union

SLEEP_TIME = 1


class Scheduler:

    def __init__(self):
        self._tasks_ready = collections.deque()
        self._tasks_delayed = []
        self._sequence = 0

    def call_soon(self, func: Callable[[...], Any], delayed: Union[int, float] = 0) -> None:
        ready = not bool(delayed)
        if delayed:
            self._sequence += 1
            deadline = time.time() + delayed
            heapq.heappush(
                self._tasks_delayed,
                (deadline, self._sequence, func)
            )
        if ready:
            self._tasks_ready.append(func)

    def run(self) -> None:

        while self._tasks_ready or self._tasks_delayed:

            if not self._tasks_ready:
                deadline, _, task = heapq.heappop(self._tasks_delayed)
                time_to_await = deadline - time.time()
                if time_to_await > 0:
                    time.sleep(time_to_await)
                self._tasks_ready.append(task)

            while self._tasks_ready:
                task = self._tasks_ready.popleft()
                task()


class QueueClosed(Exception):
    pass


class Result:
    def __init__(self, value: Any = None, exc: Exception = None):
        self._value = value
        self._exc = exc

    def get_result(self):
        if self._exc:
            raise self._exc
        return self._value


class AsyncQueue:

    def __init__(self, schler: Scheduler):
        self._scheduler = schler
        self._items = collections.deque()
        self._waiting = collections.deque()
        self._closed = False

    def close(self):
        self._closed = True
        if self._waiting and not self._items:
            for func in self._waiting:
                self._scheduler.call_soon(func)

    def put(self, item) -> None:
        if self._closed:
            raise QueueClosed()
        self._items.append(item)
        if self._waiting:
            func = self._waiting.popleft()
            self._scheduler.call_soon(func)

    def get(self, callback: Callable[[...], Any]) -> None:
        if self._closed:
            callback(Result(exc=QueueClosed()))
            return
        if self._items:
            item = self._items.popleft()
            callback(Result(value=item))
            return
        self._waiting.append(lambda: self.get(callback))


def producer_call_back_based(schler: Scheduler, aqu: AsyncQueue, amount: int) -> None:
    def _produce(n):
        if n <= amount:
            print(f'Produced {n}')
            aqu.put(n)
            schler.call_soon(
                lambda: _produce(n + 1),
                SLEEP_TIME
            )
            return
        print(f'Producer done. Now that we have a close method, '
              f'we do not need a none sentinel anymore.')
        aqu.close()

    _produce(0)


def consumer_call_back_based(schler: Scheduler, aqu: AsyncQueue) -> None:
    def _consume(result_from_producer):
        try:
            item = result_from_producer.get_result()
            print(f'Consumed {item}')
            schler.call_soon(lambda: consumer_call_back_based(schler, aqu))
        except QueueClosed:
            print(f'Queue appeared to be closed. Consumer done.')

    aqu.get(callback=_consume)


if __name__ == '__main__':
    scheduler = Scheduler()
    q = AsyncQueue(scheduler)
    scheduler.call_soon(
        lambda: producer_call_back_based(scheduler, q, 10)
    )
    scheduler.call_soon(
        lambda: consumer_call_back_based(scheduler, q)
    )
    scheduler.run()
