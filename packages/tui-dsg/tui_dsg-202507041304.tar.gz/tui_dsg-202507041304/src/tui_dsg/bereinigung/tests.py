from datetime import datetime

import numpy as np
import pandas as pd
from checkmarkandcross import image
from pandas.api.types import is_datetime64_any_dtype as is_datetime


def aufgabe1(df: pd.DataFrame):
    return image(isinstance(df, pd.DataFrame)
                 and len(df) == 1443
                 and 'show_id' in df
                 and 'type' in df
                 and 'tmdb_ref' in df
                 and 'release' in df
                 and 'runtime' in df
                 and 'episode_count' in df
                 and 'popularity' in df
                 and 'revenue' in df
                 and df['title'].dtype == object
                 and df['title'][5] == "Marvel Studios' Ant-Man and the Wasp"
                 and df['release'].dtype == object
                 and df['release'][3] == '19-03-11')


def aufgabe2(df: pd.DataFrame):
    return image(isinstance(df, pd.DataFrame)
                 and len(df) == 1443
                 and df['type'][1438] == 'Movie'
                 and df['type'][2] == 'TV Show')


def aufgabe3(df: pd.DataFrame):
    if not isinstance(df, pd.DataFrame) or 'release' not in df:
        return image(False)

    series = df['release']
    if not is_datetime(series):
        return image(False)

    return image(
        series[12] == datetime(year=2008, month=9, day=8)
        and series[122] == datetime(year=1955, month=10, day=3)
        and series[123] == datetime(year=2018, month=9, day=5)
    )


def aufgabe4(df: pd.DataFrame):
    if not isinstance(df, pd.DataFrame) or 'revenue' not in df:
        return image(False)

    return image(
        df['revenue'][0] == 'mittel'
        and df['revenue'][3] == 'unbekannt'
        and df['revenue'][5] == 'hoch'
        and df['revenue'][22] == 'mittel'
        and df['revenue'][23] == 'unbekannt'
        and df['revenue'][1412] == 'niedrig'
        and df['revenue'][1420] == 'unbekannt'
        and df['revenue'][1424] == 'mittel'
    )


def aufgabe5(avg_movie_runtime: float, avg_tvshow_runtime: float):
    return image(
        isinstance(avg_movie_runtime, float)
        and 72 < avg_movie_runtime < 73
        and isinstance(avg_tvshow_runtime, float)
        and 29 < avg_tvshow_runtime < 30
    )


def aufgabe6(df: pd.DataFrame):
    return image(
        isinstance(df, pd.DataFrame)
        and 'popularity' in df
        and abs(df['popularity'][0] - 1.891798) < 1e-6
        and abs(df['popularity'][2] - 83.259699) < 1e-6
        and abs(df['popularity'][17] - 0.315418) < 1e-6
        and abs(df['popularity'][43] - 2.479387) < 1e-6
        and abs(df['popularity'][49] - 1.106349) < 1e-6
        and abs(df['popularity'][1393] - 3.262500) < 1e-6
        and abs(df['popularity'][1400] - 24.240286) < 1e-6
        and abs(df['popularity'][1424] - 1.450903) < 1e-6
        and abs(df['popularity'][1434] - 2.355534) < 1e-6
        and abs(df['popularity'][1439] - 0.805549) < 1e-6
    )
