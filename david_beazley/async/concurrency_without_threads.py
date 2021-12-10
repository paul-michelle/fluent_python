import collections
import time
from typing import Callable, Any, Tuple, Union

SLEEP_TIME = 1


class Scheduler:

    def __init__(self):
        self._tasks_ready = collections.deque()
        self._tasks_delayed = []

    def run_soon(self, func: Callable[[...], Any], delay: Union[int, float] = 0) -> None:
        ready = not bool(delay)
        if delay:
            deadline = time.time() + delay
            self._tasks_delayed.append(
                (deadline, func)
            )
            self._tasks_delayed.sort()
        if ready:
            self._tasks_ready.append(func)

    def run(self) -> None:

        while self._tasks_ready or self._tasks_delayed:

            if not self._tasks_ready:
                deadline, task = self._tasks_delayed.pop(0)
                time_to_await = deadline - time.time()
                if time_to_await > 0:
                    time.sleep(time_to_await)
                self._tasks_ready.append(task)

            while self._tasks_ready:
                task = self._tasks_ready.popleft()
                task()


def count_down(scheduler: Scheduler, start: int = 0) -> None:
    if start >= 0:
        print(f'Down {start}')
        scheduler.run_soon(
            lambda: count_down(scheduler, start - 1),
            delay=SLEEP_TIME * 2,
        )



def count_up(scheduler: Scheduler, start: int = 0, stop: int = 0) -> None:

    def _do() -> None:
        nonlocal start
        if start <= stop:
            print(f'Up {start}')
            start += 1
            scheduler.run_soon(
                lambda: _do(),
                delay=SLEEP_TIME
            )

    _do()


if __name__ == '__main__':
    schler = Scheduler()
    schler.run_soon(lambda: count_down(schler, start=5))
    schler.run_soon(lambda: count_up(schler, stop=5))

    try:
        schler.run()
    except KeyboardInterrupt:
        pass
