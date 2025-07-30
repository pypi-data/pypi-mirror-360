import math
from heapq import heappush, heappop
from typing import Dict

import networkx as nx

from .html import graph_to_html
from .. import color_primary, color_secondary, color_error
from ..jpanim import JupyterAnimation


class Dijkstra(JupyterAnimation):
    def __init__(self, graph: nx.Graph, start_node: str):
        self._graph: nx.Graph = graph
        self._layout: Dict = nx.spring_layout(graph)
        self._start_node: str = start_node

        html, css = graph_to_html(graph, self._layout, weights='d')
        frames = self._alg()

        html += '<div class="visit-list">Als nächstes: [{{ frame.visit_list }}]</div>'

        super().__init__(html, frames, css)

    def _alg(self) -> Dict[str, Dict]:
        result = {}
        queue = [(0, self._start_node, None)]

        # initialization
        for node in self._graph:
            self._graph.nodes[node]['visited'] = False
            self._graph.nodes[node]['distance'] = 0 if node == self._start_node else math.inf

        result['Initialisierung'] = {
            **{
                f'name_{node}': f'{node} ({self._graph.nodes[node]["distance"]} / {"T" if self._graph.nodes[node]["visited"] else "F"})'
                for node in self._graph.nodes
            },
            **{
                f'node_{node}': {
                    'backgroundColor': '#cacaca'
                }
                for node in self._graph.nodes
            },
            **{
                f'edge_{source}_{target}': {
                    'backgroundColor': '#eaeaea'
                }
                for source in self._graph.nodes
                for target in self._graph.nodes
            },
            'visit_list': ', '.join(f'{v[0]} ({v[1]})' for v in queue)
        }

        # actual dijkstra
        while len(queue) > 0:
            # visit node
            node_distance_to_start, node, parent = heappop(queue)

            if self._graph.nodes[node]['visited']:
                self._graph.nodes[node]['visited'] = True

                result[f'Überspringe {node}'] = {
                    **{
                        f'name_{node}': f'{node} ({self._graph.nodes[node]["distance"]} / {"T" if self._graph.nodes[node]["visited"] else "F"})'
                        for node in self._graph.nodes
                    },
                    **{
                        f'node_{n}': {
                            'backgroundColor': f'rgb({color_error})' if n == node else '#cacaca'
                        }
                        for n in self._graph.nodes
                    },
                    'visit_list': ', '.join(f'{v[0]} ({v[1]})' for v in queue)
                }
                continue
            else:
                self._graph.nodes[node]['visited'] = True

                result[f'Besuche {node}'] = {
                    **{
                        f'name_{node}': f'{node} ({self._graph.nodes[node]["distance"]} / {"T" if self._graph.nodes[node]["visited"] else "F"})'
                        for node in self._graph.nodes
                    },
                    **{
                        f'node_{n}': {
                            'backgroundColor': f'rgb({color_primary})' if n == node else '#cacaca'
                        }
                        for n in self._graph.nodes
                    },
                    **{
                        f'edge_{source}_{target}': {
                            'backgroundColor': '#eaeaea'
                        }
                        for source in self._graph.nodes
                        for target in self._graph.nodes
                    },
                    'visit_list': ', '.join(f'{v[0]} ({v[1]})' for v in queue)
                }

            for neighbor in self._graph.neighbors(node):
                node_distance_to_neighbor = self._graph.get_edge_data(node, neighbor)['d']
                neighbor_distance_to_start = node_distance_to_start + node_distance_to_neighbor

                if neighbor_distance_to_start < self._graph.nodes[neighbor]['distance']:
                    self._graph.nodes[neighbor]['distance'] = neighbor_distance_to_start
                    heappush(queue, (neighbor_distance_to_start, neighbor, node))

                result[f'Erfasse {neighbor} von {node}'] = {
                    **{
                        f'name_{node}': f'{node} ({self._graph.nodes[node]["distance"]} / {"T" if self._graph.nodes[node]["visited"] else "F"})'
                        for node in self._graph.nodes
                    },
                    **{
                        f'node_{n}': {
                            'backgroundColor': f'rgb({color_primary})' if n == node else f'rgb({color_secondary})' if n == neighbor else '#cacaca'
                        }
                        for n in self._graph.nodes
                    },
                    **{
                        f'edge_{source}_{target}': {
                            'backgroundColor': f'rgb({color_secondary})' if (source, target) in ((node, neighbor), (neighbor, node)) else '#eaeaea'
                        }
                        for source in self._graph.nodes
                        for target in self._graph.nodes
                    },
                    'visit_list': ', '.join(f'{v[0]} ({v[1]})' for v in queue)
                }

        # finalization
        result[f'Ende durch leere Prioritätenliste'] = {
            **{
                f'node_{n}': {
                    'backgroundColor': '#cacaca'
                }
                for n in self._graph.nodes
            },
            **{
                f'edge_{source}_{target}': {
                    'backgroundColor': '#eaeaea'
                }
                for source in self._graph.nodes
                for target in self._graph.nodes
            }
        }

        return result
