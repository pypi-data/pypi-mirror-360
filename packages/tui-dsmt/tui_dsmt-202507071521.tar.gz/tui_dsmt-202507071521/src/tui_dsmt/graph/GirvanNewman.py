from typing import Dict

import networkx as nx

from .html import graph_to_html
from .. import all_colors
from ..jpanim import JupyterAnimation


class GirvanNewman(JupyterAnimation):
    def __init__(self, graph: nx.Graph):
        self._graph: nx.Graph = graph
        self._layout: Dict = nx.spring_layout(graph)

        html, css = graph_to_html(graph, self._layout, display_height='26rem', node_width='4rem', node_height='2rem')
        frames = self._alg()

        super().__init__(html, frames, css)

    def _alg(self) -> Dict[str, Dict]:
        frames = {}

        graph = self._graph.copy()
        component_colors = {
            tuple(sorted(c)): i
            for i, c in enumerate(nx.connected_components(graph))
        }

        # initialization
        frames['Graph'] = {
            **{
                f'name_{n}': f'{n}'
                for n in graph.nodes
            },
            **{
                f'node_{n}': {
                    'color': 'whitesmoke',
                    'backgroundColor': self._node_color(n, component_colors)
                }
                for n in graph.nodes
            },
            **{
                f'edge_{source}_{target}': {
                    'backgroundColor': 'rgba(0, 0, 0, 0.5)',
                }
                for source in graph.nodes
                for target in graph.nodes
            }
        }

        # iterations
        for i in range(1, len(graph.edges)):
            betweenness = self.edge_betweenness(graph)

            # betweenness
            min_betweenness = min(betweenness.values())
            max_betweenness = max(betweenness.values())

            frames[f'Iteration {i}: Berechne Kantenbetweenness-Zentralität'] = {
                f'edge_{source}_{target}': {
                    'backgroundColor': self._edge_color_betweenness(
                        betweenness.get((min(source, target), max(source, target)), 0),
                        min_betweenness, max_betweenness
                    ) if (source, target) in graph.edges else 'rgba(0, 0, 0, 0.05)',
                    'color': 'black' if (source, target) in graph.edges else 'transparent',
                    'text': f'{betweenness.get((min(source, target), max(source, target)), 0):.3f}'
                }
                for source in graph.nodes
                for target in graph.nodes
            }

            if max_betweenness - min_betweenness < 1e-8:
                frames['Ende des Algorithmus'] = {
                    f'edge_{source}_{target}': {
                        'backgroundColor': f'rgba(0, 0, 0, {0.5 if (source, target) in graph.edges else 0.05})',
                    }
                    for source in graph.nodes
                    for target in graph.nodes
                }

                break

            # remove edge
            max_betweenness_edge = max(betweenness, key=betweenness.get)
            max_u, max_v = max_betweenness_edge

            frames[f'Iteration {i}: Entferne Kante zwischen {max_u} und {max_v}'] = {
                f'edge_{source}_{target}': {
                    'backgroundColor': self._edge_color_highlight(
                        source, target, max_u, max_v
                    ) if (source, target) in graph.edges else 'rgba(0, 0, 0, 0.05)',
                    'color': self._edge_color_highlight(
                        source, target, max_u, max_v
                    ) if (source, target) in graph.edges else 'transparent',
                    'text': f'{betweenness.get((min(source, target), max(source, target)), 0):.3f}'
                }
                for source in graph.nodes
                for target in graph.nodes
            }

            if max_betweenness_edge in graph.edges:
                graph.remove_edge(max_u, max_v)
            else:
                graph.remove_edge(max_v, max_u)

            # color components
            new_components = set(tuple(sorted(c)) for c in nx.connected_components(graph))

            if any(c not in component_colors for c in new_components):
                for c in list(component_colors.keys()):
                    if c not in new_components:
                        del component_colors[c]

                for c in new_components:
                    if c not in component_colors:
                        component_colors[c] = min(i
                                                  for i in range(len(new_components))
                                                  if i not in set(component_colors.values()))

                frames[f'Iteration {i}: Neue Komponente'] = {
                    f'edge_{max_u}_{max_v}': {
                        'backgroundColor': 'rgba(0, 0, 0, 0.05)',
                        'color': 'transparent',
                    },
                    f'edge_{max_v}_{max_u}': {
                        'backgroundColor': 'rgba(0, 0, 0, 0.05)',
                        'color': 'transparent',
                    },
                    **{
                        f'node_{n}': {
                            'color': 'whitesmoke',
                            'backgroundColor': self._node_color(n, component_colors)
                        }
                        for n in graph.nodes
                    }
                }

        return frames

    @staticmethod
    def edge_betweenness(graph: nx.Graph):
        edges = {(min(u, v), max(u, v)): 0 for u, v in graph.edges}
        num_of_shortest_paths = 0

        for u in graph.nodes:
            for v in graph.nodes:
                if u < v:
                    try:
                        for path in nx.all_shortest_paths(graph, u, v):
                            num_of_shortest_paths += 1

                            for s, t in zip(path, path[1:]):
                                edges[min(s, t), max(s, t)] += 1
                    except nx.NetworkXNoPath:
                        pass

        return {e: v / num_of_shortest_paths for e, v in edges.items()}

    @staticmethod
    def _node_color(n, component_colors):
        for component, i in component_colors.items():
            if n in component:
                color = all_colors[i % len(all_colors)]
                return f'rgb({color})'

    @staticmethod
    def _edge_color_betweenness(v, v_min, v_max) -> str:
        if v_max - v_min < 1e-12:
            alpha = 1.0
        else:
            alpha = (v - v_min) / (v_max - v_min) * 0.8 + 0.2

        return f'rgba(255, 0, 0, {alpha})'

    @staticmethod
    def _edge_color_highlight(u, v, max_u, max_v):
        if min(u, v) == max_u and max(u, v) == max_v:
            return 'red'
        else:
            return 'rgba(0, 0, 0, 0.5)'
