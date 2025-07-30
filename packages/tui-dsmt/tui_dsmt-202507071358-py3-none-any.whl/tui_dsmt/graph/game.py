import random
import string
from typing import Tuple, List

import networkx as nx

from .html import graph_to_html
from ..jpanim import JupyterAnimation


def guess_adj_list(size: int = 5):
    Gs, selected = _create(size)
    selected_G = Gs[selected]

    # create adjacency list
    adj_list = []
    for node in selected_G:
        neighbors = ', '.join(selected_G.neighbors(node))
        adj_list.append(f'{node} -> [{neighbors}]')

    adj_list_str = '\n'.join(adj_list)

    # draw
    return _draw(Gs, selected, adj_list_str)


def guess_adj_matrix(size: int = 5):
    Gs, selected = _create(size)
    selected_G = Gs[selected]

    # create adjacency list
    adj_matrix = [
        [
            1 if selected_G.has_edge(u, v) else 0
            for v in selected_G
        ]
        for u in selected_G
    ]

    adj_matrix_rows = '\n '.join('[' + '  '.join(map(str, row)) + ']' for row in adj_matrix)
    adj_matrix_str = f'[{adj_matrix_rows}]'

    # draw
    return _draw(Gs, selected, adj_matrix_str)


def _create(size: int) -> Tuple[List[nx.Graph], int]:
    # prepare three graphs
    nodes = [string.ascii_uppercase[i] for i in range(size)]
    Gs = []

    for i in range(3):
        G = nx.Graph()
        Gs.append(G)

        for n in nodes:
            G.add_node(n)

        for n in nodes:
            for o in nodes:
                if n < o and random.random() < 0.4 + i * 0.1:
                    G.add_edge(n, o)

    # select one
    selected = random.randint(0, 2)

    # return
    return Gs, selected


def _draw(Gs: List[nx.Graph], selected: int, pre: str):
    selected_G = Gs[selected]

    html0, css0 = graph_to_html(Gs[0], nx.spring_layout(Gs[0]),
                               display_height='15rem', node_width='2rem', node_height='2rem')
    html1, css1 = graph_to_html(Gs[1], nx.spring_layout(Gs[1]),
                               display_height='15rem', node_width='2rem', node_height='2rem')
    html2, css2 = graph_to_html(Gs[2], nx.spring_layout(Gs[2]),
                               display_height='15rem', node_width='2rem', node_height='2rem')

    return JupyterAnimation(
        f'''
                <div class="triplets">
                    <div>
                        {html0}
                        <input type="checkbox" :disabled="frame.checkbox.disabled"
                               :style="frame.checkbox.disabled ? frame.checkbox.c1 : null"
                               @click="frame.checkbox.disabled = true">
                    </div>
                    <div>
                        {html1}
                        <input type="checkbox" :disabled="frame.checkbox.disabled"
                               :style="frame.checkbox.disabled ? frame.checkbox.c2 : null"
                               @click="frame.checkbox.disabled = true">
                    </div>
                    <div>
                        {html2}
                        <input type="checkbox" :disabled="frame.checkbox.disabled"
                               :style="frame.checkbox.disabled ? frame.checkbox.c3 : null"
                               @click="frame.checkbox.disabled = true">
                    </div>
                </div>
                <pre>{pre}</pre>
            ''',
        {
            'First': {
                **{
                    f'edge_{n}_{o}': {
                        'backgroundColor': '#aaaaaa'
                    }
                    for n in selected_G
                    for o in selected_G
                },
                **{
                    f'name_{n}': n
                    for n in selected_G
                },
                **{
                    f'node_{n}': {
                        'backgroundColor': 'hsl(189, 90%, 40%)',
                        'color': 'whitesmoke'
                    }
                    for n in selected_G
                },
                'checkbox': {
                    'disabled': False,
                    'c1': {
                        'boxShadow': f'0 0 0.5rem 0 {"green" if selected == 0 else "red"}'
                    },
                    'c2': {
                        'boxShadow': f'0 0 0.5rem 0 {"green" if selected == 1 else "red"}'
                    },
                    'c3': {
                        'boxShadow': f'0 0 0.5rem 0 {"green" if selected == 2 else "red"}'
                    }
                }
            }
        },
        [
            '''
                .triplets {
                    display: flex;
                    flex-direction: row;
                }

                .triplets > div {
                    flex-grow: 1;
                    padding: 0 2rem;

                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }

                .triplets > div:first-child {
                    padding-left: 0;
                }

                .triplets > div:last-child {
                    padding-right: 0;
                }

                .triplets > div:not(:last-child) {
                    border-right: 1px solid #bebebe;
                }

                .triplets input {
                    margin: 1rem 0;
                }
            ''',
            css0,
            css1,
            css2
        ]
    )
