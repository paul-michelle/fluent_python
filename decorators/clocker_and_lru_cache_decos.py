"""Benefiting from a built-in list recently used cache decorator.

1. Implement a Clocker - a class-based timing deco.
2. Define a recursive f(n) getting nth fib number.
3. Time get_fibo without @functools.lru_cache.
4. Time get_fibo with @functools.lru_cache.
"""
import time
import sys
from functools import wraps, lru_cache
from typing import Callable, Any, Optional

DEFAULT_FMT = '[{time_elapsed:0.2f}ms] {func_name}({func_args}) -> {exe_results}'


class Clocker:

    def __init__(self, fmt: str = DEFAULT_FMT):
        self._fmt = fmt

    def __call__(self, func: Callable[[...], Any]) -> Callable[[...], Any]:
        @wraps(func)
        def clocked_func(*_args, **_kwargs) -> Any:
            start_time = time.perf_counter_ns()
            exe_results = func(*_args, **_kwargs)
            time_elapsed = (time.perf_counter_ns() - start_time) / 10 ** 6
            if time_elapsed > 10 ** 3:
                raise TimeoutError('1 sec maximum exceeded')
            func_name = func.__name__
            args = [str(arg) for arg in _args]
            kwargs = ([f'{k} = {v}' for k, v in _kwargs.items()])
            func_args = ', '.join(args + kwargs)

            print(self._fmt.format(**locals()))
            return exe_results

        return clocked_func


@Clocker()
def get_fibo(n: int = 0) -> Optional[int]:
    if n < 2:
        return n
    try:
        return get_fibo(n - 2) + get_fibo(n - 1)
    except TimeoutError:
        return


@lru_cache()
@Clocker()
def get_fibo_cached(n: int = 0) -> int:
    if n < 2:
        return n
    return get_fibo_cached(n - 2) + get_fibo_cached(n - 1)


def main(n: int = 0, cached: bool = False):
    if cached:
        return get_fibo_cached(n)
    return get_fibo(n)


if __name__ == '__main__':
    sys.setrecursionlimit(100_000)
    main(
        n=6000,
        cached=sys.argv[-1] == '--cached'
    )

# [657.23ms] get_fibo(21) -> 10946 :: else 1 sec maximum gets exceeded
# [615.13ms] get_fibo_cached(5_000) -> ...
# [942.67ms] get_fibo_cached(6000) -> .. :: else 1 sec maximum gets exceeded
