import random
from typing import Dict

import networkx as nx

from .html import graph_to_html
from .. import color_primary, color_error, hsl_colors
from ..jpanim import JupyterAnimation


class LabelPropagation(JupyterAnimation):
    def __init__(self, graph: nx.Graph):
        self._graph: nx.Graph = graph
        self._layout: Dict = nx.spring_layout(graph)

        html, css = graph_to_html(graph, self._layout, display_height='26rem', node_width='4rem', node_height='2rem')
        frames = self._alg()

        super().__init__(html, frames, css)

    def _alg(self) -> Dict[str, Dict]:
        frames = {}

        # initialization
        frames['Graph'] = {
            **{
                f'name_{n}': f'{n}'
                for n in self._graph.nodes
            },
            **{
                f'node_{n}': {
                    'backgroundColor': self._node_color(n, None, (), None)
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

        # labels
        for node in self._graph:
            self._graph.nodes[node]['label'] = node

        frames['Initiale Labels'] = {
            **{
                f'name_{node}': f'{node} ({self._graph.nodes[node]["label"]})'
                for node in self._graph.nodes
            },
            **{
                f'node_{n}': {
                    'backgroundColor': self._node_color(n, None, (), self._graph.nodes[n]['label'])
                }
                for n in self._graph.nodes
            }
        }

        # iterations
        changes = True
        round = 0

        while changes:
            changes = False
            round += 1

            nodes = list(self._graph.nodes)
            random.shuffle(nodes)

            for node in nodes:
                neighbors = tuple(self._graph.neighbors(node))

                frames[f'Iteration {round}, Knoten {node}: Nachbarn'] = {
                    **{
                        f'node_{n}': {
                            'backgroundColor': self._node_color(n, node, neighbors, self._graph.nodes[n]['label'])
                        }
                        for n in self._graph.nodes
                    }
                }

                neighbor_labels = {}
                for neighbor in neighbors:
                    n_label = self._graph.nodes[neighbor]['label']
                    neighbor_labels[n_label] = neighbor_labels.get(n_label, 0) + 1

                mc_labels_max = max(neighbor_labels.values())
                mc_labels = [nl for nl in neighbor_labels if neighbor_labels[nl] == mc_labels_max]
                mc_label = random.choice(mc_labels)

                if mc_label != self._graph.nodes[node]['label']:
                    self._graph.nodes[node]['label'] = mc_label
                    changes = True

                    frames[f'Iteration {round}, Knoten {node}: Anpassung des Labels'] = {
                        **{
                            f'name_{n}': f'{n} ({self._graph.nodes[n]["label"]})'
                            for n in self._graph.nodes
                        },
                        **{
                            f'node_{n}': {
                                'backgroundColor': self._node_color(n, node, (), self._graph.nodes[n]['label'], True)
                            }
                            for n in self._graph.nodes
                        }
                    }
                else:
                    frames[f'Iteration {round}, Knoten {node}: Beibehalten des Labels'] = {
                        **{
                            f'node_{n}': {
                                'backgroundColor': self._node_color(n, node, (), self._graph.nodes[n]['label'], True)
                            }
                            for n in self._graph.nodes
                        }
                    }

        frames[f'Ende des Algorithmus'] = {
            **{
                f'node_{n}': {
                    'backgroundColor': self._node_color(n, None, (), self._graph.nodes[n]['label'], f=2)
                }
                for n in self._graph.nodes
            }
        }

        return frames

    @staticmethod
    def _node_color(n, current, neighbors, label, highlight=False, f=5):
        if label is None:
            return '#eaeaea'
        elif n == current:
            if highlight:
                f = 1
            else:
                return f'rgb({color_error})'
        elif n in neighbors:
            return f'rgb({color_primary})'

        h, s, l = hsl_colors[label % len(hsl_colors)]
        l = 100 - (100 - l) // f
        return f'hsl({h}, {s}%, {l}%)'
