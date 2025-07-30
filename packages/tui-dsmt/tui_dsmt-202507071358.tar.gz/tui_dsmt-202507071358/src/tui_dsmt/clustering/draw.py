import pandas as pd
from ipywidgets import interact
import plotly.express as px


def draw(df: pd.DataFrame, x='x', y='y', color='c'):
    @interact(Klassen=False)
    def _(Klassen):
        return px.scatter(df, x=x, y=y, color=(color if Klassen else None))
