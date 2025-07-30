from itertools import chain, combinations
from typing import Set

import networkx as nx

from .html import graph_to_html
from ..jpanim import JupyterAnimation


class Hall(JupyterAnimation):
    def __init__(self, graph: nx.Graph, A: Set[str], B: Set[str]):
        pos = nx.bipartite_layout(graph, A)

        # graph to html
        html, css = graph_to_html(graph, pos,
                                  max_width='30rem', display_height='20rem',
                                  node_width='2rem', node_height='2rem')

        frames = {}

        # algorithm from A to B
        frames['Prüfe alle S ⊆ A'] = {
            **{
                f'name_{node}': node
                for node in graph.nodes
            },
            **{
                f'node_{node}': self._node_color(node)
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
            }
        }

        for S in self._powerset(A):
            N = self._neighbors(graph, S)
            if len(N) == 0:
                continue

            valid = len(S) <= len(N)

            S_str = ','.join(S)
            N_str = ','.join(N)
            sign = '≤' if valid else '≰'

            frames[f'|{{{S_str}}}| {sign} |{{{N_str}}}|'] = {
                **{
                    f'node_{node}': self._node_color(node, S, N, valid)
                    for node in graph.nodes
                },
                **{
                    f'edge_{u}_{v}': self._edge_color(u, v, S, N, valid)
                    for u in graph.nodes
                    for v in graph.nodes
                }
            }

        # algorithm from B to A
        frames['Prüfe alle S ⊆ B'] = {
            **{
                f'name_{node}': node
                for node in graph.nodes
            },
            **{
                f'node_{node}': self._node_color(node)
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
            }
        }

        for S in self._powerset(B):
            N = self._neighbors(graph, S)
            if len(N) == 0:
                continue

            valid = len(S) <= len(N)

            S_str = ','.join(S)
            N_str = ','.join(N)
            sign = '≥' if valid else '≱'

            frames[f'|{{{N_str}}}| {sign} |{{{S_str}}}|'] = {
                **{
                    f'node_{node}': self._node_color(node, S, N, valid)
                    for node in graph.nodes
                },
                **{
                    f'edge_{u}_{v}': self._edge_color(u, v, S, N, valid)
                    for u in graph.nodes
                    for v in graph.nodes
                }
            }

        # initialize parent
        super().__init__(html, frames, css)

    @staticmethod
    def _node_color(node, subset=(), neighbors=(), valid=True):
        if node in subset:
            return {
                'backgroundColor': '#636EFA' if valid else '#EF553B',
                'color': 'whitesmoke'
            }
        if node in neighbors:
            return {
                'backgroundColor': 'hsl(235, 93.8%, 85%)' if valid else 'hsl(9, 85%, 75%)',
                'color': 'whitesmoke'
            }
        else:
            return {
                'backgroundColor': 'whitesmoke'
            }

    @staticmethod
    def _edge_color(u, v, subset=(), neighbors=(), valid=True):
        if u in subset and v in neighbors or v in subset and u in neighbors:
            return {
                'backgroundColor': '#636EFA' if valid else '#EF553B',
                'size': 1,
            }
        else:
            return {
                'backgroundColor': '#dddddd',
                'size': 1,
            }

    @staticmethod
    def _powerset(s):
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

    @staticmethod
    def _neighbors(G: nx.Graph, N):
        nbs = set()
        for node in N:
            nbs.update(G.neighbors(node))

        return nbs
