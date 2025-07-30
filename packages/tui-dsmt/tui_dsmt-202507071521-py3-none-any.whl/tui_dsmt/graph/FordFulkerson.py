from typing import Dict

import networkx as nx

from .MaximumFlow import MaximumFlow
from ..jpanim import JupyterAnimation


class FordFulkerson(JupyterAnimation):
    def __init__(self, graph: nx.DiGraph,
                 source: str = 's', target: str = 't',
                 capacity: str = 'capacity',
                 pos: Dict = None):
        self.graph: nx.DiGraph = graph
        self.source: str = source
        self.target: str = target
        self.capacity: str = capacity

        # residual graph
        self.residual_graph: nx.DiGraph = nx.DiGraph()
        for u, v in graph.edges:
            cv = graph.get_edge_data(u, v)['capacity']
            self.residual_graph.add_edge(u, v, capacity=cv, flow=0)
            self.residual_graph.add_edge(v, u, capacity=0, flow=0)

        # algorithm
        frames = {
            'Initialisierung': {
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
                    f'edge_{u}_{v}': self.edge_style(u, v)
                    for u, v in graph.edges
                }
            }
        }

        path_counter = {}
        while True:
            for path, uv_path, bottleneck in self.augmented_paths():
                path_str = '-'.join(path)

                if path_str not in path_counter:
                    path_counter[path_str] = 1
                    path_extension = ''
                else:
                    path_counter[path_str] += 1
                    path_extension = f' (Iteration {path_counter[path_str]})'

                frames[f'Pfad {path_str} mit Flaschenhals {bottleneck}{path_extension}'] = {
                    f'edge_{u}_{v}': self.edge_style(u, v, uv_path, bottleneck)
                    for u, v in graph.edges
                }

                for u, v in uv_path:
                    self.residual_graph.edges[u, v]['flow'] += bottleneck
                    self.residual_graph.edges[v, u]['flow'] -= bottleneck

                frames[f'Fluss entlang Pfad {path_str} anpassen{path_extension}'] = {
                    f'edge_{u}_{v}': self.edge_style(u, v, uv_path, force_color='#AAAAAA')
                    for u, v in graph.edges
                }

                break
            else:
                break

        final_name, final_status = self.final()
        frames[final_name] = final_status

        # initialize parent
        html, css, _ = MaximumFlow.draw(graph, pos, source, target, '', capacity)
        super().__init__(html, frames, css)

    def augmented_paths(self):
        c, f = self.capacity, 'flow'

        # sort paths using length to explain problems with arbitrary
        # path choosing
        sorted_paths = self.sort_paths(nx.all_simple_paths(self.residual_graph, self.source, self.target))

        # yield augmented paths
        for path in sorted_paths:
            uv_path = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            bottleneck = min(
                self.residual_graph.get_edge_data(u, v)[c] - self.residual_graph.get_edge_data(u, v)[f]
                for u, v in uv_path
            )

            if bottleneck > 0:
                yield path, uv_path, bottleneck

    def edge_style(self, u: str, v: str, path=None, bottleneck=None, force_color=None):
        flow = self.residual_graph.get_edge_data(u, v)['flow']
        capacity = self.residual_graph.get_edge_data(u, v)[self.capacity]
        text = f'{flow}/{capacity}'

        if path is not None and ((u, v) in path or (v, u) in path):
            if capacity - flow == bottleneck:
                return {
                    'backgroundColor': 'rgb(239, 85, 59)' if force_color is None else force_color,
                    'size': 2,
                    'text': text
                }
            else:
                return {
                    'backgroundColor': 'rgb(99, 110, 250)' if force_color is None else force_color,
                    'size': 2,
                    'text': text
                }
        else:
            return {
                'backgroundColor': '#AAAAAA',
                'size': 1,
                'text': text
            }

    def final(self):
        return 'Ende des Algorithmus', {
            f'edge_{u}_{v}': self.edge_style(u, v)
            for u, v in self.graph.edges
        }

    @staticmethod
    def sort_paths(paths):
        return sorted(paths, key=len, reverse=True)
