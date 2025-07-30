import networkx as nx

from .html import graph_to_html
from .. import color_primary, color_error
from ..jpanim import JupyterAnimation


class BronKerbosch(JupyterAnimation):
    def __init__(self, graph: nx.Graph):
        self.graph: nx.Graph = graph

        start_R = set()
        start_P = set(graph.nodes)
        start_X = set()

        # html
        pos = nx.spring_layout(graph)
        html, css = graph_to_html(graph, pos,
                                  max_width='40rem', display_height='20rem',
                                  node_width='2rem', node_height='2rem')

        # generate frames
        self.i: int = 0
        self.result: int = 0

        frames = {
            'Graph': {
                **{
                    f'name_{node}': node
                    for node in graph.nodes
                },
                **{
                    f'node_{node}': self.node_style(node, start_R, start_P, start_X)
                    for node in graph.nodes
                },
                **{
                    f'edge_{u}_{v}': {
                        'backgroundColor': 'gray',
                        'size': 1
                    }
                    for u, v in graph.edges
                },
                'R_text': self.set_to_str(start_R),
                'P_text': self.set_to_str(start_P),
                'X_text': self.set_to_str(start_X),
            }
        }

        for title, R, P, X in self.bron_kerbosch(start_R, start_P, start_X):
            if title in frames:
                raise AssertionError(f'{title} already used')
            frames[title] = {
                **{
                    f'node_{node}': self.node_style(node, R, P, X)
                    for node in graph.nodes
                }
            }

        # prepare animation
        super().__init__(html, frames, css)

    def bron_kerbosch(self, R, P, X, stack=()):
        if len(P) == 0 and len(X) == 0:
            self.result += 1
            yield f'Ergebnis {self.result}', R, P, X

        for v in list(P):
            neighbors = set(self.graph.neighbors(v))

            new_R = R.union({v})
            new_P = P.intersection(neighbors)
            new_X = X.intersection(neighbors)

            self.i += 1
            i = self.i
            yield f'Schritt {i}', new_R, new_P, new_X

            yield from self.bron_kerbosch(new_R.copy(), new_P.copy(), new_X.copy())

            yield f'Rückschritt zu {i}', new_R, new_P, new_X

            P.remove(v)
            X.add(v)

    @staticmethod
    def set_to_str(X):
        values = ','.join(map(str, X))
        return f'{{{values}}}'

    @staticmethod
    def node_style(node, R, P, X):
        if node in R:
            node_color = f'rgb({color_primary})'
        elif node in P:
            node_color = 'gray'
        elif node in X:
            node_color = f'rgb({color_error})'
        else:
            node_color = 'black'

        return {
            'backgroundColor': node_color,
            'color': 'whitesmoke'
        }
