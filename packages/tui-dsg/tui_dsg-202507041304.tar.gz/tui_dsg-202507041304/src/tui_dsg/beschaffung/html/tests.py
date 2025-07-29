from typing import List

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from checkmarkandcross import image


def aufgabe1_1(page: BeautifulSoup):
    return image(isinstance(page, BeautifulSoup)
                 and page.find('title').text.startswith('Geschichte des Kinos')
                 and page.find('title').text.endswith('Wikipedia'))


def aufgabe1_2(links: ResultSet):
    if not isinstance(links, ResultSet):
        return image(False)

    internal_links = 0
    for link in links:
        if link.has_attr('href') and link['href'].startswith('/wiki/'):
            internal_links += 1

    return image(internal_links > 100)


def aufgabe1_3(refs: List[str]):
    my_refs = [
        '/wiki/Schaubude',
        '/wiki/Kino',
        '/wiki/Fernsehen',
        '/wiki/Stereoskop',
        '/wiki/3D',
        '/wiki/Thomas_Alva_Edison',
        '/wiki/Kinetoskop',
        '/wiki/Filmprojektor',
        '/wiki/Bewegte_Bilder',
        '/wiki/Stummfilm',
        '/wiki/Tonfilm',
        '/wiki/Wanderkino',
        '/wiki/Erster_Weltkrieg',
        '/wiki/Filmstar',
        '/wiki/Geschichte_des_Farbfilms',
        '/wiki/Autokino'
    ]
    return image(isinstance(refs, list)
                 and len(refs) > 100
                 and all([ref in refs for ref in my_refs]))
