from typing import List

from checkmarkandcross import image


def aufgabe1(text: str):
    for start, stop, test in (
            (179119, 179158, 'hmieden, der sich am Schaden weidet und'),
            (127210, 127265, 'und spat; Und meine Mutter ist in allen Stücken So akku'),
            (3728, 3769, 'nd, wie in Hungersnot um Brot an Bäckertü'),
            (109482, 109540, 'ie welke Hand geküßt. Ich fühl o Mädchen, deinen Geist Der'),
            (72060, 72121, 't. Den schlepp ich durch das wilde Leben, Durch flache Unbede'),
            (55604, 55647, 'macht dir Pein? Ei sage mir, du Sohn der Hö')
    ):
        if test != text[start:stop].replace('\n', ' '):
            return image(False)

    return image(True)


def aufgabe2_1(count: int):
    return image(count == 4142)


def aufgabe2_2(count: int):
    return image(count == 4545)


def aufgabe3(no104: str):
    return image(
        no104.startswith('FAUST.\n') and no104.endswith('Gewißheit einem neuen Bunde?')
    )


def aufgabe4(words: List[str]):
    return image(
        len(words) == 737
        and 'Narrheit' in words
        and 'Tageszeit' in words
        and 'abgetrieben' in words
        and 'aufgerieben' in words
        and 'Mephisto' in words
        and 'Zauberei' in words
        and 'hereingesprungen' in words
        and 'Walpurgisnachtstraum' in words
    )
