"""Accumulating average value calculator with generators.

Values not stored, rather an average is calculated each time the avg-function receives new data.
With 'stop' sent instead of another number, calculation gets terminated and the final accumulated
value is returned,

Constraint: sent values should be convertible to float, commas instead of dots when
numeric in a string form are allowed.
"""
from typing import Generator, Union, Any, Callable


def gen_suspended(func: Callable[[...], Generator[Any, Any, Any]]) \
        -> Callable[[...], Generator[Any, Any, Any]]:
    def inner(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.send(None)
        return gen

    return inner


def count_average_and_freeze() -> Generator[float, Union[int, float, str], float]:
    total, count, average = 0, 0, 0.0

    while True:
        try:
            received = yield average
            if received == 'stop':
                continue
            if isinstance(received, str):
                try:
                    received = float(received.strip().replace(',', '.'))
                except ValueError:
                    print('n should be numeric')
            total += received
            count += 1
            average = round(total / count, 2)

        except GeneratorExit:
            break

    return average


@gen_suspended
def avg(gen: Generator[float, Union[int, float, str], float] = count_average_and_freeze()) -> \
        Generator[float, Union[int, float, str], float]:

    received = yield from gen
    final_average = 0.0

    if received == 'stop':
        try:
            gen.throw(GeneratorExit)
        except StopIteration as e:
            final_average = e.value

    return final_average
