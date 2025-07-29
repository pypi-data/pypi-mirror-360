from typing import Dict

from checkmarkandcross import image


def aufgabe1(letters: Dict[str, int]):
    return image(isinstance(letters, dict)
                 and letters['y'] == 524
                 and letters['W'] == 260)


def aufgabe2(number_of_duplicate_entries: int):
    return image(number_of_duplicate_entries == 0)
