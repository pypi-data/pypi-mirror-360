import random
from typing import List, Tuple
import math

import networkx as nx

from .. import color_primary, color_error, colors
from ..graph.html import graph_to_html
from ..jpanim import JupyterAnimation


class PAM(JupyterAnimation):
    def __init__(self, dataset: List[Tuple[int, int]], k: int):
        # generate a fully connected graph
        graph = nx.Graph()

        for x1, y1 in dataset:
            for x2, y2 in dataset:
                if x1 == x2 and y1 == y2:
                    continue

                did1, did2 = self._did(x1, y1), self._did(x2, y2)
                graph.add_edge(did1, did2)

        # generate a layout
        pos = {}

        min_x, max_x = min(x for x, _ in dataset), max(x for x, _ in dataset)
        min_y, max_y = min(y for _, y in dataset), max(y for _, y in dataset)

        for x, y in dataset:
            did = self._did(x, y)

            pos_x = (x - min_x) / (max_x - min_x)
            pos_y = 1 - (y - min_y) / (max_y - min_y)

            pos[did] = (pos_x, pos_y)

        # create frames from pam
        frames = {k: f for k, f in self.do_pam(dataset, k)}

        # initialize super
        html, css = graph_to_html(graph, pos,
                                  node_width='0.5rem', node_height='0.5rem',
                                  display_height='30rem')

        super().__init__(f'''
            {html}
            
            <div style="position: absolute; right: 1rem; bottom: 1rem">
                TD: {{{{ frame.td_value }}}}
            </div>
        ''', frames, css)

    @staticmethod
    def _dist(o1, o2):
        return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(o1, o2)))

    @staticmethod
    def _did(x, y) -> str:
        return f'd_{int(x * 100)}_{int(y * 100)}'

    @staticmethod
    def _node(n, medoids):
        if n in medoids:
            return {
                'backgroundColor': f'rgb({color_error})'
            }
        else:
            cl_n = min(range(len(medoids)), key=lambda i: PAM._dist(medoids[i], n))
            return {
                'backgroundColor': f'rgb({colors[cl_n]})'
            }

    @staticmethod
    def _edge(n1, n2, medoids):
        # if both or none is a medoid
        if n1 in medoids and n2 in medoids or n1 not in medoids and n2 not in medoids:
            return {
                'backgroundColor': 'transparent'
            }

        # make n1 the medoid and n2 the non-medoid
        if n2 in medoids:
            n1, n2 = n2, n1

        # get closest medoid to n2
        cl_n2 = min(medoids, key=lambda x: PAM._dist(x, n2))

        # n1 is not the closest medoid to n2
        if cl_n2 != n1:
            return {
                'backgroundColor': 'transparent'
            }

        # n1 is the closest medoid to n2
        else:
            return {
                'backgroundColor': 'black',
                'size': 0.5
            }

    @staticmethod
    def do_pam(dataset: List[Tuple[int, int]], k: int):
        # init
        medoids = random.sample(dataset, k=k)

        yield 'Zufällige Initialisierung', {
            'td_value': PAM._td(dataset, medoids),
            **{
                f'node_{PAM._did(*n)}': PAM._node(n, medoids)
                for n in dataset
            },
            **{
                f'edge_{PAM._did(*n1)}_{PAM._did(*n2)}': PAM._edge(n1, n2, medoids)
                for n1 in dataset
                for n2 in dataset
            }
        }

        # pam main loop
        delta_TD = -math.inf
        while delta_TD < 0:
            TD = PAM._td(dataset, medoids)
            best_pair, delta_TD = None, math.inf

            for i, M in enumerate(medoids):
                for N in dataset:
                    if M == N:
                        continue

                    medoids[i] = N

                    TD_MN = PAM._td(dataset, medoids)
                    if delta_TD > TD_MN - TD:
                        best_pair = (i, N)
                        delta_TD = TD_MN - TD

                    medoids[i] = M

            if delta_TD < 0:
                i, N = best_pair
                M = medoids[i]
                medoids[i] = N

                M_str = '(' + ', '.join(map(str, M)) + ')'
                N_str = '(' + ', '.join(map(str, N)) + ')'

                yield f'Vertausche {M_str} und {N_str} mit ΔTD = {delta_TD:.01f}', {
                    'td_value': PAM._td(dataset, medoids),
                    **{
                        f'node_{PAM._did(*n)}': PAM._node(n, medoids)
                        for n in dataset
                    },
                    **{
                        f'edge_{PAM._did(*n1)}_{PAM._did(*n2)}': PAM._edge(n1, n2, medoids)
                        for n1 in dataset
                        for n2 in dataset
                    }
                }

            else:
                yield 'ΔTD > 0', {}

    @staticmethod
    def _td(dataset, medoids):
        clusters = [
            min(
                (i for i in range(len(medoids))),
                key=lambda i: PAM._dist(o, medoids[i])
            )
            for o in dataset
        ]

        td = sum(PAM._dist(o, medoids[i]) for o, i in zip(dataset, clusters))

        return td
