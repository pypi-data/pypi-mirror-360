from typing import Callable

import numpy as np
import pandas as pd
import plotly.express as px
from ipywidgets import interact, IntSlider
from sklearn.cluster import KMeans


def animate_kmeans(fun: Callable, data: pd.DataFrame, max_frames: int = 30, threshold: float = 1e-8, **kwargs):
    result = {
        'x': [],
        'y': [],
        'type': [],
        'class': [],
        'group': [],
        'frame': []
    }

    old_x = None
    old_y = None

    for i, (centroids_x, centroids_y) in enumerate(fun(data['x'], data['y'], **kwargs), 1):
        result['x'].extend(data['x'].tolist())
        result['y'].extend(data['y'].tolist())
        result['type'].extend((0.1 for _ in range(len(data['x']))))

        for x, y in zip(data['x'], data['y']):
            distances = np.sqrt((centroids_x - x) ** 2 + (centroids_y - y) ** 2)
            result['class'].append(str(distances.argmin() + 1))

        result['x'].extend(centroids_x)
        result['y'].extend(centroids_y)
        result['type'].extend((0.5 for _ in range(len(centroids_x))))
        result['class'].extend(map(str, range(1, len(centroids_x) + 1)))

        combined_length = len(data['x']) + len(centroids_x)
        result['group'].extend(range(combined_length))
        result['frame'].extend((i for _ in range(combined_length)))

        if i >= max_frames:
            break

        if old_x is not None and old_y is not None:
            if np.sum(np.abs(old_x - centroids_x)) + np.sum(np.abs(old_y - centroids_y)) < threshold:
                break

        old_x = centroids_x.copy()
        old_y = centroids_y.copy()

    return px.scatter(result, x='x', y='y',
                      animation_frame='frame', animation_group='group',
                      color='class', symbol='type', size='type',
                      color_discrete_sequence=px.colors.qualitative.Light24)


def interactive_kmeans(data: pd.DataFrame):
    @interact(k=IntSlider(15, 1, 30, 1))
    def _(k):
        df = data[['x', 'y']]
        df['c'] = KMeans(k).fit_predict(df).astype(str)

        return px.scatter(df, x='x', y='y', color='c',
                          color_discrete_sequence=px.colors.qualitative.Light24)
