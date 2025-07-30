from typing import Dict

import networkx as nx

from .html import graph_to_html
from ..jpanim import JupyterAnimation


class DFS(JupyterAnimation):
    def __init__(self, graph: nx.Graph, start_node: str):
        self._graph: nx.Graph = graph
        self._layout: Dict = nx.spring_layout(graph)
        self._start_node: str = start_node

        html, css = graph_to_html(graph, self._layout)
        frames = self._alg()

        super().__init__(html, frames, css)

    def _alg(self) -> Dict[str, Dict]:
        result = {}

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
            }
        }

        # actual dfs
        current_nodes = []
        current_path = []

        def dfs(current_node, depth=0):
            self._graph.nodes[current_node]['visited'] = True

            color_lightness = sum((50 / 2 ** i for i in range(depth + 1)))
            color = f'hsl(189, 90%, {color_lightness}%)'

            if current_nodes:
                key = f'Besuche {current_node} von {current_nodes[-1]}'
            else:
                key = f'Besuche {current_node}'

            current_nodes.append(current_node)

            result[key] = {
                f'name_{current_node}': f'{current_node} ({depth})',
                f'node_{current_node}': {
                    'backgroundColor': color
                },
                **{
                    f'edge_{s}_{t}': {
                        'backgroundColor': '#FF7F00' if (min(s, t), max(s, t)) in current_path else '#EAEAEA'
                    }
                    for s in self._graph.nodes
                    for t in self._graph.nodes
                }
            }

            for neighbor in self._graph.neighbors(current_node):
                if self._graph.nodes[neighbor]['visited']:
                    continue

                path = min(current_node, neighbor), max(current_node, neighbor)
                current_path.append(path)
                dfs(neighbor, depth + 1)
                current_path.pop()

            current_nodes.pop()
            if current_nodes:
                result[f'Zurück zu {current_nodes[-1]} von {current_node}'] = {
                    f'edge_{s}_{t}': {
                        'backgroundColor': '#FF7F00' if (min(s, t), max(s, t)) in current_path[:-1] else '#EAEAEA'
                    }
                    for s in self._graph.nodes
                    for t in self._graph.nodes
                }

        dfs(self._start_node)

        # finalization
        result[f'Ende der Rekursion'] = {
            **{
                f'edge_{source}_{target}': {
                    'backgroundColor': '#eaeaea'
                }
                for source in self._graph.nodes
                for target in self._graph.nodes
            }
        }

        return result
