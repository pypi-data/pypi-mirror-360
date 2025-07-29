from typing import Callable

from checkmarkandcross import image


def aufgabe1(fun: Callable[[int], int]):
    return image(
        callable(fun)
        and fun(50) == 5
        and fun(256) == 13
        and fun(7507) == 19
    )


def aufgabe2(fun: Callable):
    return image(
        callable(fun)
        and fun(1, 12, 3, 4) == (4, 1, 12)
        and fun(637, 994, 713) == (3, 637, 994)
    )
