import pandas as pd
import plotly.express as px
from ipywidgets import interact, FloatSlider, IntSlider
from sklearn.cluster import KMeans, DBSCAN


def interactive_kmeans(data: pd.DataFrame):
    @interact(k=IntSlider(15, 1, 30, 1))
    def _(k):
        df = data[['x', 'y']]
        df['c'] = KMeans(k).fit_predict(df).astype(str)

        return px.scatter(df, x='x', y='y', color='c',
                          color_discrete_sequence=px.colors.qualitative.Light24)


def interactive_dbscan(data: pd.DataFrame):
    @interact(eps=FloatSlider(value=2.4, min=0.1, max=10, step=0.1),
              min_samples=IntSlider(value=5, min=1, max=20, step=1))
    def _(eps, min_samples):
        df = data[['x', 'y']].copy()
        df['c'] = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(df).astype(str)

        return px.scatter(df, x='x', y='y', color='c',
                          color_discrete_sequence=px.colors.qualitative.Light24)
