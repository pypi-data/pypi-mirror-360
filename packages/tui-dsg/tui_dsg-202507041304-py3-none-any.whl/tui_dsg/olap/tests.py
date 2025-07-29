import pandas as pd
from checkmarkandcross import image


def aufgabe1(df: pd.DataFrame):
    return image(
        isinstance(df, pd.DataFrame)
        and 'show_id' in df
        and 'type' in df
        and 'title' in df
        and 'release' in df
        and 'runtime' in df
        and 'episode_count' in df
        and 'popularity' in df
        and 'avg_runtime' in df
        and df['show_id'][3] == 's536'
        and df['runtime'][1438] == 86.
    )


def aufgabe2(cube: pd.Series):
    return image(
        isinstance(cube, pd.Series)
        and cube.index[177] == ('1928-11', 'kurz', 104.0, 'TV Show')
        and cube.index[876] == ('1932-07', 'kurz', 57.0, 'Movie')
        and 5.4 < cube['2017-03']['kurz'][12]['TV Show'] < 5.7
    )


def aufgabe3(cube: pd.Series):
    return image(
        isinstance(cube, pd.Series)
        and cube.index.names == ['type', 'release', 'episode_count', 'avg_runtime']
    )


def aufgabe4(cube: pd.Series):
    return image(
        isinstance(cube, pd.Series)
        and cube.index.names == ['release', 'episode_count', 'avg_runtime']
    )


def aufgabe5(cube: pd.Series):
    return image(
        isinstance(cube, pd.Series)
        and (
                cube.index.names == ['release', 'episode_count', 'avg_runtime']
                or cube.index.names == [None, 'episode_count', 'avg_runtime']
        )
        and 2.09 < (cube['1955' if '1955' in cube else 1995][26]['kurz']) < 2.1
    )
