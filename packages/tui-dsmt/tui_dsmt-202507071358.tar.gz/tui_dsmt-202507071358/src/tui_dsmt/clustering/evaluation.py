import pandas as pd
import plotly.express as px
from ipywidgets import interact, IntSlider
from sklearn.cluster import KMeans


def TD2(df, centroids):
    cx = df['cluster'].map(lambda i: centroids[i][0])
    cy = df['cluster'].map(lambda i: centroids[i][1])

    return sum((df['x'] - cx) ** 2 + (df['y'] - cy) ** 2)


def s(df, o):
    df['d'] = (df['x'] - o['x']) ** 2 + (df['y'] - o['y']) ** 2

    o_cluster = df[df['cluster'] == o['cluster']]
    a = o_cluster['d'].sum() / (len(o_cluster) - 1)

    other_clusters = df[df['cluster'] != o['cluster']]
    min_dist = other_clusters.groupby('cluster')['d'].sum().nsmallest(1)

    next_cluster_id = min_dist.index[0]
    next_cluster_d, = min_dist
    next_cluster_size = len(df[df['cluster'] == next_cluster_id])

    b = next_cluster_d / next_cluster_size

    return (b - a) / max(a, b)


def S(df):
    df['s'] = df.apply(lambda o: s(df, o), axis=1)
    return df['s'].sum() / len(df)


def interactive_td2(data: pd.DataFrame):
    @interact(k=IntSlider(15, 1, 30, 1))
    def _(k):
        df = data.copy()

        kmeans = KMeans(k)
        kmeans.fit(df)

        df['cluster'] = kmeans.predict(df)
        df['color'] = df['cluster'].astype(str)

        return px.scatter(df, x='x', y='y', color='color',
                          title=f'TD2 = {TD2(df, kmeans.cluster_centers_)}',
                          color_discrete_sequence=px.colors.qualitative.Light24)


def td2_graph(data: pd.DataFrame):
    def calc_td2_for(k):
        df = data.copy()
        kmeans = KMeans(k).fit(df)
        df['cluster'] = kmeans.predict(df)

        return TD2(df, kmeans.cluster_centers_)

    return px.bar(pd.DataFrame({
        'k': range(1, 41),
        'td2': (calc_td2_for(k) for k in range(1, 41))
    }), x='k', y='td2', log_y=True)


def silhouette_graph(data: pd.DataFrame, random_state: int = 1):
    def calc_S_for(k):
        df = data.copy()
        df['cluster'] = KMeans(k, random_state=random_state).fit_predict(df)
        return S(df)

    return px.bar(pd.DataFrame({
        'k': range(2, 30),
        'S': (calc_S_for(k) for k in range(2, 30))
    }), x='k', y='S')
