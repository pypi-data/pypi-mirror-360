import random

import networkx as nx

from .html import graph_to_html
from .. import color_secondary, hsl_color_error
from ..jpanim import JupyterAnimation


class RandomWalk(JupyterAnimation):
    def __init__(self, graph: nx.Graph, steps: int = 50):
        # generate html from graph
        pos = nx.spring_layout(graph)
        html, css = graph_to_html(graph, pos,
                                  display_height='30rem',
                                  node_width='2rem', node_height='2rem')

        # pre-calculate all steps and track heat
        all_nodes = list(graph.nodes)

        next_node = random.choice(all_nodes)
        next_heat = {
            node: 1 if node == next_node else 0
            for node in all_nodes
        }

        path = [(next_node, next_heat)]

        for i in range(steps):
            all_neighbors = list(graph.neighbors(next_node))

            next_node = random.choice(all_neighbors)
            next_heat = {
                node: next_heat[node] + (1 if node == next_node else 0)
                for node in all_nodes
            }

            path.append((next_node, next_heat))

        # normalize heat map
        max_value = max(next_heat.values())
        for _, heat in path:
            for n in heat:
                heat[n] /= max_value

        # generate frames
        frames = {}

        for i, (node, heat) in enumerate(path, start=0):
            if i == 0:
                frame_title = f'Zufälliger Startknoten {node}'
            else:
                frame_title = f'Schritt {i}'

            frames[frame_title] = {
                **{
                    f'name_{n}': str(n)
                    for n in graph.nodes
                },
                **{
                    f'node_{n}': {
                        'backgroundColor': self.color_node(n, node, heat)
                    }
                    for n in graph.nodes
                },
                **{
                    f'edge_{n1}_{n2}': {
                        'backgroundColor': 'black'
                    }
                    for n1 in graph.nodes
                    for n2 in graph.nodes
                }
            }

        frames['Ende des Walk'] = {
            f'node_{n}': {
                'backgroundColor': self.color_node(n, None, path[-1][1])
            }
            for n in graph.nodes
        }

        super().__init__(html, frames, css, fast_forward=(steps > 50))

    @staticmethod
    def color_node(node, current, heat):
        if node == current:
            return f'rgb({color_secondary})'
        else:
            h, s, l = hsl_color_error
            s = heat[node] * 100

            return f'hsl({h}, {s}%, {l}%)'
