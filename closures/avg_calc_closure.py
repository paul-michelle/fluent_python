from statistics import mean
from typing import Callable, Union, List


def make_averager() -> Callable[[Union[float, int, List[Union[float, int]]]], float]:
    stored_values = []

    def calculate_avg(received_data: Union[float, int, List[Union[float, int]]]) -> float:
        if isinstance(received_data, float) or isinstance(received_data, int):
            received_data = [received_data]
        stored_values.extend(
            [x for x in received_data if isinstance(x, int) or isinstance(x, float)]
        )
        return mean(stored_values)

    return calculate_avg


if __name__ == '__main__':
    avg = make_averager()
    another_avg = make_averager()
    if (
            avg([1, 1.5, 3.5, 'fizz']) == 2
            and 'stored_values' not in avg.__code__.co_varnames
            and avg.__code__.co_freevars[0] == 'stored_values'
            and avg.__closure__[0] != another_avg.__closure__[0]
    ):
        avg.__closure__[0].cell_contents.clear()
        avg.__closure__[0].cell_contents.append('buzz')
    try:
        avg(1)
    except TypeError:
        print("As Van Rossum put it, we're all adults here...")


