from typing import Tuple, Dict

import networkx as nx

from .html import graph_to_html
from ..jpanim import JupyterAnimation


class MaximumFlow(JupyterAnimation):
    def __init__(self, graph: nx.DiGraph, source: str = 's', target: str = 't', capacity: str = 'capacity'):
        html, css, frames = self.draw(graph, None, source, target, 'Initialisierung', capacity)
        super().__init__(html, frames, css)

    @staticmethod
    def draw(graph, pos: Dict = None,
             source: str = 's', target: str = 't',
             frame_name: str = '', capacity: str = 'capacity') -> Tuple[str, str, Dict]:
        # positions
        if pos is None:
            graph_copy = graph.copy()
            graph_copy.remove_nodes_from((source, target))

            pos = nx.spring_layout(graph_copy)

            xs = [x for x, _ in pos.values()]
            ys = [y for _, y in pos.values()]

            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            dx, dy = max_x - min_x, max_y - min_y

            pos[source] = [min_x - dx / 2, max_y - dy / 2]
            pos[target] = [max_x + dx / 2, max_y - dy / 2]

        # graph to html
        html, css = graph_to_html(graph, pos,
                                  max_width='40rem', display_height='20rem',
                                  node_width='2rem', node_height='2rem')

        # frames
        frames = {
            frame_name: {
                **{
                    f'name_{node}': node
                    for node in graph.nodes
                },
                **{
                    f'node_{node}': {
                        'backgroundColor': '#EF553B' if node in ('s', 't') else '#636EFA',
                        'color': 'whitesmoke'
                    }
                    for node in graph.nodes
                },
                **{
                    f'edge_{u}_{v}': {
                        'backgroundColor': 'rgb(99, 110, 250)',
                        'size': 1,
                        'text': f'0/{graph.get_edge_data(u, v)[capacity]}'
                    }
                    for u, v in graph.edges
                }
            }
        }

        # return all
        return html, css, frames
