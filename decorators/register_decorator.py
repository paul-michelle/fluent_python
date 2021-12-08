"""PyCon-2017 (Portland, Oregon, May 17-25).

Romalho Luciano giving an example of a simple register
decorator as his lecture 'Decorators and Descriptors Decoded'.
"""

import calendar
import time
from typing import List, Callable, Any

commands = {}


def first_letter_deco(func: Callable[[...], Any]) \
        -> Callable[[...], Any]:
    first_letter = func.__name__[0]
    if func.__name__[0:4] == 'get_':
        first_letter = func.__name__[4]
    commands[first_letter] = func
    return func


@first_letter_deco
def get_time() -> None:
    print(time.strftime('%H:%M:%S'))


@first_letter_deco
def day() -> None:
    print(time.strftime('%A, %B, %d, %Y'))


@first_letter_deco
def month_calendar():
    curr_year, curr_month = time.localtime()[:2]
    calendar.prmonth(curr_year, curr_month)


@first_letter_deco
def year_calendar():
    current_year = time.localtime()[0]
    calendar.prcal(current_year)


def main(argv: List[str]) -> None:
    def give_hint() -> None:
        print(f"Flags of {argv[0]} : {'|'.join(sorted(commands))}")

    try:
        letter = argv[1]
        commands.get(letter, give_hint)()
    except IndexError:
        give_hint()


if __name__ == '__main__':
    import sys

    main(sys.argv)
