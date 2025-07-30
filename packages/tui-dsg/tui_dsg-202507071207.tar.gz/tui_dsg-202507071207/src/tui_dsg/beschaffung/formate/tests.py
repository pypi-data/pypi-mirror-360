from typing import List, Dict

from checkmarkandcross import image


def aufgabe1_1(csv_data: List[List[str]]):
    return image(isinstance(csv_data, list)
                 and len(csv_data) == 1451
                 and csv_data[0] == ['title', 'release_year']
                 and csv_data[212] == ['Growing Fangs', '2021'])


def aufgabe1_2(releases_per_year: Dict[str, int]):
    return image(isinstance(releases_per_year, dict)
                 and len(releases_per_year) == 90
                 and releases_per_year['2012'] == 41)


def aufgabe2_1(json_data: List[Dict]):
    return image(isinstance(json_data, list)
                 and len(json_data) == 1450
                 and json_data[56] == {'title': 'Rookie of the Year',
                                       'cast': ['Thomas Ian Nicholas',
                                                'Gary Busey',
                                                'Albert Hall',
                                                'Amy Morton',
                                                'Dan Hedaya',
                                                'Eddie Bracken']})


def aufgabe2_2(most_frequent_actor: str):
    return image(most_frequent_actor == 'Jim Cummings')
