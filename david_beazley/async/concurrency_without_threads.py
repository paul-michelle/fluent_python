import collections
import time
from typing import Callable, Any, Tuple, Union

SLEEP_TIME = .5


class Scheduler:

    def __init__(self):
        self._tasks = collections.deque()

    def run_soon(self, funcs: Union[Callable[[...], Any], Tuple[Callable[[...], Any]]]) -> None:
        if not isinstance(funcs, tuple):
            funcs = (funcs,)
        self._tasks.extend(funcs)

    def run(self) -> None:
        while self._tasks:
            task = self._tasks.popleft()
            task()


def count_down(start: int, scheduler: Scheduler) -> None:
    if start >= 0:
        print(start)
        time.sleep(SLEEP_TIME)
        scheduler.run_soon(lambda: count_down(start - 1, scheduler))


def count_up(scheduler: Scheduler, start: int = 0, stop: int = 0) -> None:

    def _print_n_sleep() -> None:
        nonlocal start
        if start <= stop:
            print(start)
            start += 1
            time.sleep(SLEEP_TIME)
            scheduler.run_soon(lambda: _print_n_sleep())

    _print_n_sleep()


def count_up_rec(scheduler: Scheduler, start: int = 0, stop: int = 0) -> None:
    if start <= stop:
        print(start)
        time.sleep(SLEEP_TIME)
        scheduler.run_soon(lambda: count_up_rec(scheduler, start + 1, stop))


if __name__ == '__main__':
    schler = Scheduler()
    schler.run_soon(
        (lambda: count_down(5, schler), lambda: count_up(schler, stop=5))
    )
    try:
        schler.run()
    except KeyboardInterrupt:
        print(
            """But then again, if there were a 20-sec sleep inside one of the two
            functions, the other function will have to wait. It is blocking.
            So, their running in turn kind of 'giving back control' is by no means enough.
            
            The funny stuff, though, is that this behaviour mimics the two generators, with
            popping a task, executing it and appending it back."""
        )
