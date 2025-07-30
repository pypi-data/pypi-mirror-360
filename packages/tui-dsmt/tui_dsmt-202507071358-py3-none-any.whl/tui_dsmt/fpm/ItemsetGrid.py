import itertools
from typing import List, Tuple, Dict

import networkx as nx

from .Itemset import Itemset
from .. import color_primary
from ..graph.html import graph_to_html
from ..jpanim import JupyterAnimation

TRANSACTION_LIST = List[Tuple[int, Itemset]]


class ItemsetGrid(JupyterAnimation):
    def __init__(self, transactions: TRANSACTION_LIST):
        self.transactions: TRANSACTION_LIST = transactions
        self.items: List[str] = sorted(set(e for _, transaction in transactions for e in transaction))

        self.itemsets: List[Itemset] = [
            Itemset(*x)
            for l in range(len(self.items) + 1)
            for x in itertools.combinations(self.items, l)
        ]

        # generate graph
        self.graph: nx.Graph = nx.Graph()

        for itemset in self.itemsets:
            if len(itemset) == 0:
                continue

            for subset in itemset.subsets(len(itemset) - 1):
                self.graph.add_edge(self._name(subset), self._name(itemset))

        # generate positions
        itemsets_per_size: Dict[int, List[Itemset]] = {}

        for itemset in self.itemsets:
            size = len(itemset)

            if size not in itemsets_per_size:
                itemsets_per_size[size] = []

            itemsets_per_size[size].append(itemset)

        pos = {}

        y_step = 1. / (len(itemsets_per_size) - 1)
        y_value = 0.

        for level in itemsets_per_size.values():
            x_step = 1. / (len(level) + 1)
            x_value = x_step

            for itemset in level:
                itemset_name = self._name(itemset)
                pos[itemset_name] = (x_value, y_value)

                x_value += x_step

            y_value += y_step

        # convert to html
        html, css = graph_to_html(self.graph, pos, display_height='30rem', node_width='6rem')

        # initialize parent
        super().__init__(html,  self._generate_frames, css)

    @staticmethod
    def _name(itemset):
        return ''.join(map(str, itemset))

    @staticmethod
    def _clear_name(itemset):
        if len(itemset) == 0:
            return '∅'
        else:
            return f'({", ".join(map(str, itemset))})'

    @property
    def _generate_frames(self):
        return {
            'Start': {
                **{
                    f'edge_{self._name(i1)}_{self._name(i2)}': {
                        'backgroundColor': 'rgba(0, 0, 0, 0.67)',
                        'size': 1
                    }
                    for i1 in self.itemsets
                    for i2 in self.itemsets
                },
                **{
                    f'node_{self._name(i1)}': {
                        'backgroundColor': f'rgb({color_primary})',
                        'color': 'whitesmoke'
                    }
                    for i1 in self.itemsets
                },
                **{
                    f'name_{self._name(i1)}': self._clear_name(i1)
                    for i1 in self.itemsets
                }
            }
        }
