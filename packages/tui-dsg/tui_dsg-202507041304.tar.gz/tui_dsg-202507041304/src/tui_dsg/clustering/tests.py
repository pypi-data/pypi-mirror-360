import pandas as pd
from checkmarkandcross import image


def aufgabe1(df: pd.DataFrame):
    tuples = list(map(tuple, df.itertuples(index=False)))

    return image(
        len(df) == 71
        and abs(tuples[37][0] - 1) < 1e-6 and abs(tuples[37][1] - 0.3572570047026176) < 1e-6
        and abs(tuples[46][0] - 0.0108695652) < 1e-6 and abs(tuples[46][1] - 0.38603992608474474) < 1e-6
        and abs(tuples[59][0] - 0.9393939393) < 1e-6 and abs(tuples[59][1] - 0.902739024068395) < 1e-6
    )


def aufgabe2(df: pd.DataFrame):
    return image(
        len(df) == 71
        and 'kmeans' in df
    )


def aufgabe3(df: pd.DataFrame):
    return image(
        len(df) == 71
        and 'dbscan' in df
    )


def aufgabe4(kmeans: float, dbscan: float):
    return image(
        isinstance(kmeans, float) and 0 < kmeans <= 1
        and isinstance(dbscan, float) and 0 < dbscan <= 1
    )
