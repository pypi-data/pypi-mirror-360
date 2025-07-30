from typing import Dict, List

import networkx as nx

from .html import graph_to_html
from ..jpanim import JupyterAnimation
from .. import hex_colors


class Kruskal(JupyterAnimation):
    def __init__(self,
                 graph: nx.Graph, pos: Dict[str, List[float]],
                 mst: nx.Graph = None, frames: dict[str, dict] = None
                 ):
        self._graph: nx.Graph = graph
        self._pos: Dict[str, List[float]] = pos

        # mirror vertically
        my_pos = {
            key: [value[0], -value[1]]
            for key, value in pos.items()
        }

        # graph to html
        html, css = graph_to_html(graph, my_pos, weights='weight', node_width='7.5rem', node_height='1.4rem')

        html += '<div v-if="frame.sum >= 0" class="weight-sum">Summe der Gewichte: {{ frame.sum }}</div>'

        css += '''
            .node-container .node {
                font-size: 0.8rem;
            }
            
            .node-container text {
                opacity: 0.8;
            }
        '''

        # MSG properties
        if mst and frames:
            self._mst: nx.Graph = mst
            self._frames: dict[str, dict] = frames

        else:
            # initialization
            sum = 0

            self._frames = {
                'Kantenloser Graph': {
                    **{
                        f'name_{node}': node
                        for node in graph.nodes
                    },
                    **{
                        f'node_{node}': {
                            'backgroundColor': '#aaaaaa'
                        }
                        for node in graph.nodes
                    },
                    **{
                        f'edge_{u}_{v}': {
                            'backgroundColor': '#dddddd',
                            'color': '#cacaca',
                            'size': 1
                        }
                        for u in graph.nodes
                        for v in graph.nodes
                    },
                    'sum': sum
                }
            }

            # algorithm
            edges = [(u, v, graph.get_edge_data(u, v)['weight']) for u, v in graph.edges]
            sorted_edges = sorted(edges, key=lambda x: x[2])

            self._mst = nx.Graph()
            self._mst.add_nodes_from(graph.nodes)

            for source, target, weight in sorted_edges:
                self._frames[f'Kante zwischen {source} und {target} betrachten'] = {
                    f'edge_{source}_{target}': {
                        'backgroundColor': 'red',
                        'color': 'gray',
                        'size': 4
                    }
                }
                self._mst.add_edge(source, target, weight=weight)

                if len(list(nx.all_simple_paths(self._mst, source, target))) >= 2:
                    self._frames[f'Kante zwischen {source} und {target} nicht aufnehmen'] = {
                        f'edge_{source}_{target}': {
                            'backgroundColor': '#aaaaaa',
                            'color': '#cacaca',
                            'size': 2
                        }
                    }
                    self._mst.remove_edge(source, target)
                else:
                    sum += weight
                    self._frames[f'Kante zwischen {source} und {target} aufnehmen'] = {
                        f'edge_{source}_{target}': {
                            'backgroundColor': 'hsl(189, 90%, 50%)',
                            'color': 'gray',
                            'size': 3
                        },
                        'sum': sum
                    }

            # finalization
            self._frames[f'Keine Kanten verbleibend'] = {}

        # initialize parent
        super().__init__(html, self._frames, css)

    def threshold(self, value: int) -> 'Kruskal':
        all_edges = [(u, v, self._graph.get_edge_data(u, v)['weight']) for u, v in self._mst.edges()]
        remove_edges = [(u, v) for u, v, w in all_edges if w > value]

        # new frames generated from all previous frames
        # hidden weight sum
        frames = {
            'Minimaler Spannbaum': {}
        }

        for frame in self._frames.values():
            frames['Minimaler Spannbaum'].update(frame)

        frames['Minimaler Spannbaum']['sum'] = -1

        # remove edges
        mst = self._mst.copy()
        mst.remove_edges_from(remove_edges)

        frames['Kanten entfernen'] = {
            f'edge_{u}_{v}': {
                'backgroundColor': 'red',
                'color': 'gray',
                'size': 3
            }
            for u, v in remove_edges
        }

        # coloring clusters
        mst_components = []
        for i, component in enumerate(nx.connected_components(mst)):
            for node in component:
                mst_components.append((node, i))

        frames['Komponenten markieren'] = {
            **{
                f'edge_{u}_{v}': {
                    'backgroundColor': '#aaaaaa',
                    'color': 'gray',
                    'size': 2
                }
                for u, v in remove_edges
            },
            **{
                f'node_{node}': {
                    'backgroundColor': hex_colors[i % len(hex_colors)]
                }
                for node, i in mst_components
            },
        }

        # new Kruskal object
        return Kruskal(self._graph, self._pos, self._mst, frames)
