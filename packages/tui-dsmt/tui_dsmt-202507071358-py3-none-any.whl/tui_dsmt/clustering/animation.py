from typing import Callable

import numpy as np
import pandas as pd
import plotly.express as px


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


def animate_dbscan(fun: Callable, data: pd.DataFrame, **kwargs):
    result = {
        'x': [],
        'y': [],
        'class': [],
        'group': [],
        'frame': []
    }

    xs = data['x']
    ys = data['y']

    for i, clusters in enumerate(fun(data['x'], data['y'], **kwargs), 1):
        result['x'].extend(xs.tolist())
        result['y'].extend(ys.tolist())
        result['class'].extend(map(str, clusters))
        result['group'].extend(range(1, len(xs) + 1))
        result['frame'].extend((i for _ in range(len(data['x']))))

    classes = set(clusters)
    i = 0

    while i < len(result['x']):
        for cl in classes:
            result['x'].insert(i, 0)
            result['y'].insert(i, 0)
            result['class'].insert(i, str(cl))
            result['group'].insert(i, -cl)
            result['frame'].insert(i, result['frame'][i])

        i += len(xs) + len(classes)

    return px.scatter(result, x='x', y='y',
                      animation_frame='frame', animation_group='group',
                      range_x=(xs.min() - 1, xs.max() + 1), range_y=(ys.min() - 1, ys.max() + 1),
                      color='class',
                      color_discrete_sequence=px.colors.qualitative.Light24)
