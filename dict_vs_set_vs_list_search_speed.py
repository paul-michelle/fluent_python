"""
Measuring speed of CONTAINS search for various
types of containers. Intel CORE i5 CPU

needles found       haystack  min time spent
during each of      scope     on search cycle
five measurements             (5 times measured)
(total - 1k needles,
0.5k are guaranteed
not to be in haystack)

                RESULTS FOR:

                    DICT

500 500 500 500 500 |    1000 | 91701 ns
500 500 500 500 500 |   10000 | 107449 ns
500 500 500 500 500 |  100000 | 102948 ns
500 500 500 500 500 | 1000000 | 185319 ns
500 500 500 500 500 |10000000 | 193323 ns

                    SET

500 500 500 500 500 |    1000 | 303197 ns
500 500 500 500 500 |   10000 | 324382 ns
500 500 500 500 500 |  100000 | 94059 ns
500 500 500 500 500 | 1000000 | 143023 ns
500 500 500 500 500 |10000000 | 195142 ns

                    LIST

500 500 500 500 500 |      1000 | 5527443 ns     | 60 times slower than dict
500 500 500 500 500 |    10_000 | 51306491 ns
500 500 500 500 500 |   100_000 | 516733338 ns
500 500 500 500 500 | 1_000_000 | 5771800301 ns
500 500 500 500 500 |10_000_000 | 58452294214 ns  | 300k (!) times slower than dict
"""

import sys
import time
from array import array
from functools import wraps
from random import (
    random, uniform
)
from typing import (
    List, Set, Dict, Union, Callable
)

MIN_EXPONENT = 3
MAX_EXPONENT = 7
HAYSTACK_SCOPE = 10 ** MAX_EXPONENT
NEEDLES_SCOPE = 500


def ns_timer(execute_times: int = 1) -> Callable[[Callable[[...], None]], Callable[[...], List[int]]]:
    def outer(func: Callable[[...], None]) -> Callable[[...], List[int]]:
        @wraps(func)
        def inner(*args, **kwargs) -> List[int]:
            measurements = []
            for i in range(execute_times):
                start_time = time.perf_counter_ns()
                func(*args, **kwargs)
                exe_time = time.perf_counter_ns() - start_time
                measurements.append(exe_time)
            return measurements

        return inner

    return outer


class RandomFloatsGenerator:

    def __init__(self, haystack_scope: int = HAYSTACK_SCOPE,
                 needles_scope: int = NEEDLES_SCOPE):
        self._haystack_scope = haystack_scope
        self._needles_scope = needles_scope
        self._load_haystack_and_needles_to_files()

    def _get_haystack_and_needles(self):
        haystack_arr = array('d', [random() for _ in range(self._haystack_scope)])
        needles_arr = array('d', [uniform(1, 2) for _ in range(self._needles_scope)])
        return haystack_arr, needles_arr

    def _load_haystack_and_needles_to_files(self):
        haystack, needles = self._get_haystack_and_needles()
        with open('auxiliary/haystack.arr', mode='wb') as f:
            haystack.tofile(f)
        with open('auxiliary/needles.arr', mode='wb') as f:
            needles.tofile(f)


class ContainersTester:

    @staticmethod
    def _set_up_data(container_type: str, size: int):
        haystack = None
        floats = array('d')
        with open('auxiliary/haystack.arr', mode='rb') as f:
            floats.fromfile(f, size)

        if container_type == 'dict':
            haystack = dict.fromkeys(floats, 0)
        if container_type == 'set':
            haystack = set(floats)
        if container_type == 'list':
            haystack = list(floats)

        needles = array('d')
        with open('auxiliary/needles.arr', mode='rb') as f:
            needles.fromfile(f, NEEDLES_SCOPE)
        needles.extend(floats[::size // 500])

        return haystack, needles

    @ns_timer(execute_times=5)
    def _search_needles(self, haystack: Union[Dict, Set, List],
                        needles: array, verbose: bool):
        found_count = 0
        for needle in needles:
            if needle in haystack:
                found_count += 1
        if verbose:
            print(found_count, end=' ')

    def test_container_speed(self, container_type: str, verbose: bool):
        for n in range(MIN_EXPONENT, MAX_EXPONENT + 1):
            size = 10 ** n
            haystack, needles = self._set_up_data(container_type, size)
            results = self._search_needles(haystack=haystack,
                                           needles=needles,
                                           verbose=verbose)
            print(
                '|{:{}d} | {} ns'.format(size, MAX_EXPONENT + 1, min(results))
            )


if __name__ == '__main__':

    generator = RandomFloatsGenerator()
    tester = ContainersTester()

    verbosity_flag = False
    if '-v' in sys.argv:
        verbosity_flag = True
        sys.argv.remove('-v')
    tester.test_container_speed(
        container_type=sys.argv[1],
        verbose=verbosity_flag
    )
