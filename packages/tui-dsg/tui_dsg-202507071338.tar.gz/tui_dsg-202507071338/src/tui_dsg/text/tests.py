import re
from typing import List

from checkmarkandcross import image
from nltk.corpus import stopwords


def aufgabe1(text: str):
    return image(isinstance(text, str)
                 and not re.findall(r'[A-Z]', text)
                 and 'this ebook is for' not in text
                 and 'project gutenberg ebook' not in text
                 and 'information about donations to the project gutenberg' not in text)


def aufgabe2(tokens: List[str]):
    return image(isinstance(tokens, list)
                 and 15_000 <= len(tokens) <= 25_000
                 and all([s not in tokens for s in stopwords.words('german')])
                 and all([s not in tokens for s in [',', ':', ';', '(', ')']]))


def aufgabe3(syllables: List[str]):
    return image(isinstance(syllables, list)
                 and 25_000 <= len(syllables) <= 35_000
                 and all([isinstance(syl, str) for syl in syllables])
                 and all([w in syllables for w in ['freund', 'gu', 'ten', 'kreis', 'wünscht']]))


def aufgabe4(top10: List[str]):
    return image(isinstance(top10, list)
                 and len(top10) == 10
                 and all([isinstance(s, str) for s in top10]))
