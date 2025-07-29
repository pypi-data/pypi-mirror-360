from types import GeneratorType
from typing import List, Callable

from checkmarkandcross import image


def aufgabe1(fun: Callable[[int], GeneratorType]):
    if not callable(fun):
        return image(False)

    gen = fun(10)

    return image(
        isinstance(gen, GeneratorType)
        and list(gen) == [0, 2, 4, 6, 8]
    )


def aufgabe2(ls: List[int]):
    return image(
        isinstance(ls, list)
        and len(ls) == 128
        and ls[0] == 0 and ls[-1] == 254
    )
