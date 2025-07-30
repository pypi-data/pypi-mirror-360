import math
import random
from typing import Dict

import networkx as nx

from .html import graph_to_html
from .. import color_primary
from ..jpanim import JupyterAnimation


class FruchtermanReingold(JupyterAnimation):
    def __init__(self,
                 graph: nx.Graph,
                 iterations: int = 100,
                 temp: float = 0.1, c: float = 0.95,
                 r=None, k=None,
                 min_temp: float = 0.01):
        if r is None:
            r = math.sqrt(1.0 / len(graph.nodes))
        if k is None:
            k = r

        html, css = graph_to_html(graph,
                                  {n: (0, 0) for n in graph.nodes},
                                  max_width='40rem', display_height='20rem',
                                  node_width='5rem', node_height='2rem',
                                  animated_positions=True)

        # Zufällige Initialisierung
        pos = {
            node: (random.random(), random.random())
            for node in graph
        }
        res = self.normalize(pos)

        frames = {
            'Initialisierung': {
                **{
                    f'name_{n}': str(n)
                    for n in graph.nodes
                },
                **{
                    f'node_{n}': {
                        'backgroundColor': f'rgb({color_primary})',
                        'color': 'whitesmoke',
                        'left': f'calc({res[n][0] * 100}% - 2.5rem)',
                        'top': f'calc({res[n][1] * 100}% - 1rem)'
                    }
                    for n in graph.nodes
                },
                **{
                    f'edge_{n1}_{n2}': {
                        'backgroundColor': 'black',
                        'x1': f'{res[n1][0] * 100}%',
                        'y1': f'{res[n1][1] * 100}%',
                        'x2': f'{res[n2][0] * 100}%',
                        'y2': f'{res[n2][1] * 100}%'
                    }
                    for n1, n2 in graph.edges
                }
            }
        }

        # Algorithmus
        for i in range(1, iterations + 1):
            delta = {}

            # abstoßend
            for u, pos_u in pos.items():
                delta[u] = (0, 0)

                for v, pos_v in pos.items():
                    if pos_u == pos_v:
                        continue

                    d = self.fr(pos_u, pos_v, r)
                    delta[u] = delta[u][0] + d[0], delta[u][1] + d[1]

            # anziehend
            for u, v in graph.edges:
                pos_u = pos[u]
                pos_v = pos[v]

                d = self.fa(pos_u, pos_v, k)

                delta[u] = delta[u][0] + d[0], delta[u][1] + d[1]
                delta[v] = delta[v][0] - d[0], delta[v][1] - d[1]

            # Kräfte anwenden
            for u in delta:
                pos[u] = pos[u][0] + delta[u][0] * temp, pos[u][1] + delta[u][1] * temp

            # normalisieren
            res = self.normalize(pos)

            # Temperatur
            temp = max(min_temp, temp * c)

            # Frame erzeugen
            frames[f'Iteration {i} (Temperatur: {temp:0.6f})'] = {
                **{
                    f'node_{n}': {
                        'backgroundColor': f'rgb({color_primary})',
                        'color': 'whitesmoke',
                        'left': f'calc({res[n][0] * 100}% - 2.5rem)',
                        'top': f'calc({res[n][1] * 100}% - 1rem)'
                    }
                    for n in graph.nodes
                },
                **{
                    f'edge_{n1}_{n2}': {
                        'backgroundColor': 'black',
                        'x1': f'{res[n1][0] * 100}%',
                        'y1': f'{res[n1][1] * 100}%',
                        'x2': f'{res[n2][0] * 100}%',
                        'y2': f'{res[n2][1] * 100}%'
                    }
                    for n1, n2 in graph.edges
                }
            }

        super().__init__(html, frames, css, fast_forward=True)

    @staticmethod
    def fr(pos_u, pos_v, r):
        uv = (pos_v[0] - pos_u[0], pos_v[1] - pos_u[1])
        m = -(r ** 2) / math.sqrt(uv[0] ** 2 + uv[1] ** 2)

        return m * uv[0], m * uv[1]

    @staticmethod
    def fa(pos_u, pos_v, k):
        uv = (pos_v[0] - pos_u[0], pos_v[1] - pos_u[1])
        m = (uv[0] ** 2 + uv[1] ** 2) / k

        return m * uv[0], m * uv[1]

    @staticmethod
    def normalize(pos: Dict):
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]

        min_x, min_y = min(xs), min(ys)
        max_x, max_y = max(xs), max(ys)

        res = {}

        for key in pos:
            res[key] = (
                (pos[key][0] - min_x) / (max_x - min_x),
                (pos[key][1] - min_y) / (max_y - min_y)
            )

        return res
