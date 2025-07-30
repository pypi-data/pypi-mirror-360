from typing import Callable

import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans


def kmeans(cluster, k=2):
    df = pd.DataFrame({
        'x': [x for x, _ in cluster],
        'y': [y for _, y in cluster]
    })
    r = KMeans(n_clusters=k).fit_predict(df)

    return tuple(
        tuple(
            p
            for p, c in zip(cluster, r)
            if i == c
        )
        for i in range(k)
    )


def _min_dist_clusters(clusters, dist: Callable):
    _, (c1, c2) = min(
        (dist(l, r), (l, r)) for l in clusters for r in clusters if l != r
    )

    return c1, c2


def AgglomerativeClustering(df: pd.DataFrame, dist: Callable):
    data = tuple((x, y) for _, (x, y) in df.iterrows())

    range_x = (min(x for x, _ in data) - 1, max(x for x, _ in data) + 1)
    range_y = (min(y for _, y in data) - 1, max(y for _, y in data) + 1)

    xs = []
    ys = []
    clusters = []
    groups = []
    frames = []

    # init
    assignment = {(x, y): str(i) for i, (x, y) in enumerate(data, start=1)}
    color_values = list(assignment.values())

    frame = 1

    for i, (x, y) in enumerate(data, start=1):
        xs.append(x)
        ys.append(y)
        clusters.append(assignment[(x, y)])
        groups.append(-i)
        frames.append(frame)

    # aggl
    candidates = set(((x, y),) for x, y in data)

    while len(candidates) >= 2:
        c1, c2 = _min_dist_clusters(candidates, dist)
        new_cluster = c1 + c2

        candidates.remove(c1)
        candidates.remove(c2)
        candidates.add(new_cluster)

        o = max(c1, c2, key=len)[0]
        for p in new_cluster:
            assignment[p] = assignment[o]

        frame += 1

        for i, (x, y) in enumerate(data, start=1):
            xs.append(x)
            ys.append(y)
            clusters.append(assignment[(x, y)])
            groups.append(-i)
            frames.append(frame)

        # fuck plotly
        for i, color in enumerate(color_values, start=1):
            xs.append(max(range_x) + 100)
            ys.append(max(range_y) + 100)
            clusters.append(color)
            groups.append(10_000_000 + i)
            frames.append(frame)

    # animation
    return px.scatter(
        pd.DataFrame({
            'x': xs,
            'y': ys,
            'cluster': clusters,
            'group': groups,
            'frame': frames
        }),
        x='x', y='y',
        animation_frame='frame', animation_group='group',
        range_x=range_x, range_y=range_y,
        color='cluster',
        color_discrete_sequence=px.colors.qualitative.Light24
    )


def _sse(cluster, dist: Callable):
    x_mean = sum(x for x, _ in cluster) / len(cluster)
    y_mean = sum(y for _, y in cluster) / len(cluster)

    sum_of_squared_error = 0
    for x, y in cluster:
        sum_of_squared_error += (x - x_mean) ** 2 + (y - y_mean) ** 2

    return sum_of_squared_error


def _max_sse_cluster(clusters, dist: Callable):
    return max(clusters, key=lambda c: _sse(c, dist))


def DivisiveClustering(df: pd.DataFrame, dist: Callable):
    data = tuple((x, y) for _, (x, y) in df.iterrows())

    xs = []
    ys = []
    clusters = []
    groups = []
    frames = []

    # init
    all_colors = set('0')

    max_cluster = 0
    assignment = {(x, y): str(max_cluster) for x, y in data}

    frame = 1

    for i, (x, y) in enumerate(data, start=1):
        xs.append(x)
        ys.append(y)
        clusters.append(assignment[(x, y)])
        groups.append(-i)
        frames.append(frame)

    # divi
    candidates = set((data,))

    while len(candidates) >= 1:
        c = _max_sse_cluster(candidates, dist)
        c1, c2 = kmeans(c, k=2)

        max_cluster += 1
        all_colors.add(max_cluster)

        for p in c2:
            assignment[p] = str(max_cluster)

        candidates.remove(c)

        if len(c1) > 1:
            candidates.add(c1)
        if len(c2) > 1:
            candidates.add(c2)

        frame += 1
        for i, (x, y) in enumerate(data, start=1):
            xs.append(x)
            ys.append(y)
            clusters.append(assignment[(x, y)])
            groups.append(-i)
            frames.append(frame)

    # plotly color fix
    min_x, max_x = min(xs) - 1, max(xs) + 1
    min_y, max_y = min(ys) - 1, max(ys) + 1

    for f in range(1, frame + 1):
        for p, c in enumerate(all_colors, start=5):
            xs.append(-p)
            ys.append(-p)
            clusters.append(c)
            groups.append(-100 * p)
            frames.append(f)

    # animation
    return px.scatter(
        pd.DataFrame({
            'x': xs,
            'y': ys,
            'cluster': clusters,
            'group': groups,
            'frame': frames
        }),
        x='x', y='y',
        animation_frame='frame', animation_group='group',
        range_x=(min_x, max_x), range_y=(min_y, max_y),
        color='cluster',
        color_discrete_sequence=px.colors.qualitative.Light24
    )
