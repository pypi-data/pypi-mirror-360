from typing import List, Tuple

from .Itemset import Itemset
from .ItemsetGrid import ItemsetGrid
from .. import color_primary, color_error

TRANSACTION_LIST = List[Tuple[int, Itemset]]


class ItemsetGridApriori(ItemsetGrid):
    def __init__(self, transactions: TRANSACTION_LIST, min_supp: int = 2):
        self.min_supp: int = min_supp
        super().__init__(transactions)

    @property
    def _generate_frames(self):
        frames = {
            'Start': {
                **{
                    f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, [])
                    for i1 in self.itemsets
                    for i2 in self.itemsets
                },
                **{
                    f'node_{self._name(i1)}': {
                        'backgroundColor': self._node_color(i1, [], []),
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

        # C1 and L1
        C1 = [i for i in self.itemsets if len(i) == 1]

        frames['C1'] = {
            **{
                f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, C1)
                for i1 in self.itemsets
                for i2 in self.itemsets
            },
            **{
                f'node_{self._name(i1)}': {
                    'backgroundColor': self._node_color(i1, C1, None),
                    'color': 'whitesmoke'
                }
                for i1 in self.itemsets
            },
        }

        L1 = [i for i in C1 if i.count_in(self.transactions) >= self.min_supp]

        frames['L1'] = {
            **{
                f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, [])
                for i1 in self.itemsets
                for i2 in self.itemsets
            },
            **{
                f'node_{self._name(i1)}': {
                    'backgroundColor': self._node_color(i1, C1, L1),
                    'color': 'whitesmoke'
                }
                for i1 in self.itemsets
            },
        }

        # algorithm
        Ls = set(L1)

        L = L1
        k = 1

        while len(L) > 0:
            k += 1

            C_joined, C_pruned = self._generiere_kandidaten(L, k)
            L = [i for i in C_pruned if i.count_in(self.transactions) >= self.min_supp]
            Ls.update(L)

            frames[f'C{k} Join'] = {
                **{
                    f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, C_joined)
                    for i1 in self.itemsets
                    for i2 in self.itemsets
                },
                **{
                    f'node_{self._name(i1)}': {
                        'backgroundColor': self._node_color(i1, C_joined, None),
                        'color': 'whitesmoke'
                    }
                    for i1 in C_joined
                }
            }

            frames[f'C{k} Pruning'] = {
                **{
                    f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, C_joined)
                    for i1 in self.itemsets
                    for i2 in self.itemsets
                },
                **{
                    f'node_{self._name(i1)}': {
                        'backgroundColor': self._node_color(i1, C_joined, C_pruned),
                        'color': 'whitesmoke'
                    }
                    for i1 in C_joined
                }
            }

            frames[f'L{k}'] = {
                **{
                    f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, [])
                    for i1 in self.itemsets
                    for i2 in self.itemsets
                },
                **{
                    f'node_{self._name(i1)}': {
                        'backgroundColor': self._node_color(i1, C_pruned, L),
                        'color': 'whitesmoke'
                    }
                    for i1 in C_pruned
                }
            }

        frames[f'Ende (L{k} ist leer)'] = {
            **{
                f'node_{self._name(i1)}': {
                    'backgroundColor': self._node_color(i1, Ls, None),
                    'color': 'whitesmoke'
                }
                for i1 in self.itemsets
            }
        }

        return frames

    @staticmethod
    def _generiere_kandidaten(L, k):
        # Join
        all_C_k = set()

        for e1 in L:
            for e2 in L:
                if e1.matches(e2, k - 2):
                    all_C_k.add(e1.union(e2))

        # Pruning
        C_k = set()

        for c in all_C_k:
            for subset in c.subsets(k - 1):
                if subset not in L:
                    break
            else:
                C_k.add(c)

        return all_C_k, C_k

    @staticmethod
    def _edge_style(i1, i2, C):
        if len(i1) >= len(i2):
            return {
                'backgroundColor': 'rgba(0, 0, 0, 0.67)',
                'size': 1
            }
        if i1 != () and i1 not in i2.subsets(len(i2) - 1):
            return {
                'backgroundColor': 'rgba(0, 0, 0, 0.67)',
                'size': 1
            }
        if i2 not in C:
            return {
                'backgroundColor': 'rgba(0, 0, 0, 0.67)',
                'size': 1
            }
        else:
            return {
                'backgroundColor': f'rgb({color_primary})',
                'size': 2
            }

    @staticmethod
    def _node_color(i1, C, L):
        if len(i1) == 0:
            return f'rgb({color_primary})'
        if i1 not in C:
            return '#AAAAAA'
        if L is not None and i1 not in L:
            return f'rgb({color_error})'

        return f'rgb({color_primary})'
