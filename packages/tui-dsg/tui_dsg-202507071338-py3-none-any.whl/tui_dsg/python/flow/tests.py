from typing import Tuple, Callable

from checkmarkandcross import image


def aufgabe1(fun: Callable[[int, int, int], Tuple[int, int, int]]):
    return image(
        callable(fun)
        and fun(3, 5, 1) == (1, 3, 5)
        and fun(5, 4, 1) == (1, 4, 5)
    )


def aufgabe2(fun: Callable[[int, int], int]):
    return image(
        callable(fun)
        and fun(11, 12) == 2
        and fun(31, 33) == 4
        and fun(21, 21) == 0
    )
