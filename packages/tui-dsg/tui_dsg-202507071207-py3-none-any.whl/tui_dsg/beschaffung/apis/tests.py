from typing import List

from checkmarkandcross import image


def aufgabe1(starships: List[str]):
    return image(len(starships) == 5
                 and 'https://swapi.dev/api/starships/31/' in starships
                 and 'https://swapi.dev/api/starships/41/' in starships)


def aufgabe2(starship_names: List[str]):
    return image(len(starship_names) == 5
                 and 'Republic Cruiser' in starship_names
                 and 'Naboo Royal Starship' in starship_names)
