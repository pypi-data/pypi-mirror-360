from checkmarkandcross import image
import pandas as pd
import numpy as np


def aufgabe1(df: pd.DataFrame):
    return image(isinstance(df, pd.DataFrame)
                 and len(df) == 1450
                 and 'show_id' in df)


def aufgabe2_1(df: pd.DataFrame):
    return image('release_after_2000' in df
                 and df['release_after_2000'].dtype == np.bool
                 and not df['release_after_2000'][1]
                 and df['release_after_2000'][16])


def aufgabe2_2(df: pd.DataFrame):
    return image('duration' not in df)


def aufgabe3(rel_movie_count: float, rel_tvshow_count: float):
    return image(isinstance(rel_movie_count, float)
                 and isinstance(rel_tvshow_count, float)
                 and rel_movie_count > 0.7
                 and rel_tvshow_count < 0.3
                 and abs(1 - rel_movie_count - rel_tvshow_count) < 1e-6)


def aufgabe4_1(df: pd.DataFrame):
    test = pd.DataFrame(['Alonso Ramirez Ramos', 'Dave Wasson', 'John Cherry', 'Karen Disher', 'Hamish Hamilton'],
                        index=[0, 0, 1, 2, 3],
                        columns=['director'])
    return image(isinstance(df, pd.DataFrame) and test.equals(df[:5]))


def aufgabe4_2(df: pd.DataFrame):
    test = pd.DataFrame(
        [
            ['Alonso Ramirez Ramos', 'Duck the Halls: A Mickey Mouse Christmas Special'],
            ['Dave Wasson', 'Duck the Halls: A Mickey Mouse Christmas Special'],
            ['John Cherry', 'Ernest Saves Christmas'],
            ['Karen Disher', 'Ice Age: A Mammoth Christmas'],
            ['Hamish Hamilton', 'The Queen Family Singalong']
        ],
        index=[0, 0, 1, 2, 3],
        columns=['director', 'title']
    )
    return image(isinstance(df, pd.DataFrame) and test.equals(df[:5]))


def aufgabe4_3(df: pd.DataFrame):
    test = pd.DataFrame(
        [
            ['Aaron Blaise', 'Brother Bear'],
            ['Adam Shankman', 'The Pacifier, Cheaper by the Dozen 2, Bedtime Stories'],
            ['Adam Stein', 'Kim Possible'],
            ['Alan Barillaro', 'Piper'],
            ['Alan Shapiro', 'The Christmas Star'],
        ],
        columns=['director', 'title']
    ).set_index('director')
    return image(isinstance(df, pd.DataFrame) and test.equals(df[:5]))
