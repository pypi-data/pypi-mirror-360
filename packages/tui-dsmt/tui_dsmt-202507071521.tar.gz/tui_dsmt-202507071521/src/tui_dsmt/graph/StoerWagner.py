import math
import random
from itertools import chain, combinations
from typing import Dict, Any, Tuple

import networkx as nx

from .html import graph_to_html
from .. import color_primary, color_secondary, color_error
from ..jpanim import JupyterAnimation


class StoerWagner(JupyterAnimation):
    def __init__(self, graph: nx.Graph, pos: Dict, start_node: Any = None):
        # store properties
        self.graph: nx.Graph = graph
        self.start_node: Any = start_node or random.choice(graph.nodes)

        for key in list(pos.keys()):
            pos[key] = pos[key][0], -pos[key][1]

        # run algorithm
        self.frames: Dict[str, Dict] = {
            'Initialisierung': {}
        }

        # last element is a duplicate
        all_graphs = [graph, *self.stoer_wagner()][:-1]

        # generate graph structure from all merged graphs
        merged_graph = nx.Graph()
        for g in all_graphs:
            for edge in g.edges:
                merged_graph.add_edge(*edge, weight=g.get_edge_data(*edge)['weight'])

        merged_pos = {}
        for g in all_graphs:
            for node in g.nodes:
                node_name = self.node_name(node)

                if node_name in pos:
                    merged_pos[node_name] = pos[node_name]
                else:
                    for a, b in self._powerset(node_name):
                        if a in merged_pos and b in merged_pos:
                            a_x, a_y = merged_pos[a]
                            b_x, b_y = merged_pos[b]

                            merged_pos[node_name] = (a_x + b_x) / 2, (a_y + b_y) / 2
                            break
                    else:
                        raise AssertionError

        html, css = graph_to_html(merged_graph, merged_pos, weights='weight',
                                  display_height='16rem', node_width='8rem')

        # fix layout
        self.frames['Initialisierung'] = {
            **{
                f'name_{self.node_name(n)}': str(n)
                for n in merged_graph.nodes
            },
            **{
                f'node_{self.node_name(n)}': {
                    'backgroundColor': 'lightgray',
                    'color': 'black'
                }
                for n in graph.nodes
            },
            **{
                f'edge_{self.node_name(n1)}_{self.node_name(n2)}': {
                    'color': 'black',
                    'backgroundColor': 'black',
                    'size': 1
                }
                for n1 in graph.nodes
                for n2 in graph.nodes
            }
        }

        for frame in self.frames.values():
            for n in merged_graph.nodes:
                nn = f'node_{self.node_name(n)}'
                if nn not in frame:
                    frame[nn] = {
                        'display': 'none'
                    }

            for n1 in merged_graph.nodes:
                for n2 in merged_graph.nodes:
                    en = f'edge_{self.node_name(n1)}_{self.node_name(n2)}'
                    if en not in frame:
                        frame[en] = {
                            'color': 'transparent',
                            'backgroundColor': 'transparent'
                        }

        # run
        super().__init__(html, self.frames, css)

    def stoer_wagner(self):
        best_weight: float = math.inf
        best_cut: nx.Graph = self.graph

        graph: nx.Graph = self.graph

        for it in range(1, len(self.graph)):
            cut, graph, weight = self.minimum_cut_phase(graph, it)
            yield graph

            if weight < best_weight:
                best_weight = weight
                best_cut = cut

        return best_cut

    def minimum_cut_phase(self, graph: nx.Graph, it: int) -> Tuple:
        S = [self.start_node]

        self.frames[f'Iteration {it}: Start mit {self.start_node}'] = {
            **{
                f'node_{self.node_name(n)}': self.node_style(n, S)
                for n in graph.nodes
            },
            **{
                f'edge_{self.node_name(n1)}_{self.node_name(n2)}': {
                    'color': 'black',
                    'backgroundColor': 'black',
                    'size': 1
                }
                for n1 in graph.nodes
                for n2 in graph.nodes
            }
        }

        s, t = None, None
        for _ in range(len(graph) - 1):
            ranking = {}

            for node in S:
                for neighbor in graph.neighbors(node):
                    if neighbor in S:
                        continue

                    edge_weight = graph.get_edge_data(node, neighbor)['weight']
                    ranking[neighbor] = ranking.get(neighbor, 0) + edge_weight

            best = max(ranking.keys(), key=ranking.get)
            S.append(best)

            self.frames[f'Iteration {it}: Erweitere um {best} mit Gewicht {ranking[best]}'] = {
                **{
                    f'node_{self.node_name(n)}': self.node_style(n, S)
                    for n in graph.nodes
                },
                **{
                    f'edge_{self.node_name(n1)}_{self.node_name(n2)}': {
                        'color': 'black',
                        'backgroundColor': f'rgb({color_primary})' if n1 in S and n2 in S else 'black',
                        'size': 1
                    }
                    for n1 in graph.nodes
                    for n2 in graph.nodes
                }
            }

            s = t
            t = best

        # cut
        cut = self.split_nodes(*S[:-1]), self.split_nodes(t)

        self.frames[f'Iteration {it}: Cut mit Gewicht {ranking[best]}'] = {
            **{
                f'node_{self.node_name(n)}': {
                    'backgroundColor': f'rgb({color_primary})' if n in S[:-1] else f'rgb({color_secondary})',
                    'color': 'white'
                }
                for n in graph.nodes
            },
            **{
                f'edge_{self.node_name(n1)}_{self.node_name(n2)}': {
                    'color': 'black',
                    'backgroundColor': f'rgb({color_error})' if n1 in S[:-1] and n2 == t or n2 in S[:-1] and n1 == t else f'rgb({color_primary})',
                    'size': 2 if n1 in S[:-1] and n2 == t or n2 in S[:-1] and n1 == t else 1
                }
                for n1 in graph.nodes
                for n2 in graph.nodes
            }
        }

        print(f'Frame {len(self.frames)}: Cut {cut[0]} | {cut[1]} mit Gewicht {ranking[best]}')

        # merge
        if s is not None:
            next_graph, merged_name = self.merge_nodes(graph, s, t)
            self.frames[f'Iteration {it}: Merge {s} und {t}'] = {
                **{
                    f'node_{self.node_name(n)}': {
                        'backgroundColor': f'rgb({color_error})' if n == merged_name else f'rgb({color_primary})',
                        'color': 'white'
                    }
                    for n in next_graph.nodes
                },
                **{
                    f'edge_{self.node_name(n1)}_{self.node_name(n2)}': {
                        'color': 'black',
                        'backgroundColor': f'rgb({color_primary})',
                        'size': 1
                    }
                    for n1 in next_graph.nodes
                    for n2 in next_graph.nodes
                }
            }
        else:
            next_graph = graph
            merged_name = None

        return cut, next_graph, ranking[best]

    @staticmethod
    def merge_nodes(graph, s, t):
        merged_name = ','.join(sorted(str(s).split(',') + str(t).split(',')))

        merged_weights = {}
        for node in (s, t):
            for neighbor in graph.neighbors(node):
                if neighbor not in (s, t):
                    edge_weight = graph.get_edge_data(node, neighbor)['weight']
                    merged_weights[neighbor] = merged_weights.get(neighbor, 0) + edge_weight

        merged_graph = graph.copy()
        merged_graph.remove_nodes_from((s, t))
        for neighbor, weight in merged_weights.items():
            merged_graph.add_edge(merged_name, neighbor, weight=weight)

        return merged_graph, merged_name

    @staticmethod
    def split_nodes(*nodes):
        return [
            y
            for node in nodes
            for y in (
                list(map(int, node.split(','))) if isinstance(node, str)
                else [node]
            )
        ]

    @staticmethod
    def _powerset(nodes):
        n = nodes.split('_')
        n_ = set(n)

        for a in chain.from_iterable(combinations(n, i) for i in range(1, len(n) // 2 + 1)):
            a_ = set(a)
            b_ = n_ - a_

            ar = sorted(a_)
            if len(ar) == 1:
                ar = int(ar[0])
            else:
                ar = '_'.join(ar)

            br = sorted(b_)
            if len(br) == 1:
                br = int(br[0])
            else:
                br = '_'.join(br)

            yield ar, br

    @staticmethod
    def node_name(n):
        return n if not isinstance(n, str) else n.replace(',', '_')

    @staticmethod
    def node_style(node, S):
        if node == S[-1]:
            return {
                'backgroundColor': f'rgb({color_error})',
                'color': 'white'
            }
        if len(S) >= 2 and node == S[-2]:
            return {
                'backgroundColor': f'rgb({color_secondary})',
                'color': 'white'
            }
        if node in S:
            return {
                'backgroundColor': f'rgb({color_primary})',
                'color': 'white'
            }

        return {
            'backgroundColor': 'lightgray',
            'color': 'black'
        }
