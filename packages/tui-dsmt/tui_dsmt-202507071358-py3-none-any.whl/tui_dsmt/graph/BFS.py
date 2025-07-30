from typing import Dict

import networkx as nx

from .html import graph_to_html
from ..jpanim import JupyterAnimation


class BFS(JupyterAnimation):
    def __init__(self, graph: nx.Graph, start_node: str):
        self._graph: nx.Graph = graph
        self._layout: Dict = nx.spring_layout(graph)
        self._start_node: str = start_node

        html, css = graph_to_html(graph, self._layout)
        frames = self._alg()

        html += '<div class="visit-list">Als nächstes: [{{ frame.visit_list }}]</div>'

        super().__init__(html, frames, css)

    def _alg(self) -> Dict[str, Dict]:
        result = {}
        visit = [(self._start_node, 0)]

        # initialization
        for node in self._graph:
            self._graph.nodes[node]['visited'] = False
            self._graph.nodes[node]['distance'] = 0

        result['Initialisierung'] = {
            **{
                f'name_{node}': node
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
            'visit_list': ', '.join((v[0] for v in visit))
        }

        # actual bfs
        while len(visit) > 0:
            current_node, current_distance = visit.pop(0)

            self._graph.nodes[current_node]['visited'] = True
            self._graph.nodes[current_node]['distance'] = current_distance

            color_lightness = sum((50 / 2 ** i for i in range(current_distance + 1)))
            result[f'Besuche {current_node}'] = {
                f'name_{current_node}': f'{current_node} ({current_distance})',
                f'node_{current_node}': {
                    'backgroundColor': f'hsl(189, 90%, {color_lightness}%)'
                },
                **{
                    f'edge_{source}_{target}': {
                        'backgroundColor': '#eaeaea'
                    }
                    for source in self._graph.nodes
                    for target in self._graph.nodes
                },
                'visit_list': ', '.join((v[0] for v in visit))
            }

            result[f'Nachbarn von {current_node}'] = {}

            for neighbor in self._graph.neighbors(current_node):
                if not self._graph.nodes[neighbor]['visited']:
                    self._graph.nodes[neighbor]['visited'] = True
                    visit.append((neighbor, current_distance + 1))

                    result[f'Nachbarn von {current_node}'][f'edge_{current_node}_{neighbor}'] = {
                        'backgroundColor': '#FFA15A'
                    }
                    result[f'Nachbarn von {current_node}'][f'edge_{neighbor}_{current_node}'] = {
                        'backgroundColor': '#FFA15A'
                    }
                else:
                    result[f'Nachbarn von {current_node}'][f'edge_{current_node}_{neighbor}'] = {
                        'backgroundColor': '#FF007F'
                    }
                    result[f'Nachbarn von {current_node}'][f'edge_{neighbor}_{current_node}'] = {
                        'backgroundColor': '#FF007F'
                    }

            result[f'Nachbarn von {current_node}']['visit_list'] = ', '.join((v[0] for v in visit))

        # finalization
        result[f'Ende durch leere Besuchsliste'] = {
            **{
                f'edge_{source}_{target}': {
                    'backgroundColor': '#eaeaea'
                }
                for source in self._graph.nodes
                for target in self._graph.nodes
            }
        }

        return result
