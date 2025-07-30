from typing import List, Tuple, Set

from .Itemset import Itemset
from .ItemsetGrid import ItemsetGrid
from .. import OrderedSet
from .. import color_primary, color_secondary, color_error, colors

TRANSACTION_LIST = List[Tuple[int, Itemset]]


class ItemsetGridECLAT(ItemsetGrid):
    def __init__(self, transactions: TRANSACTION_LIST, min_supp: int = 2):
        self.min_supp: int = min_supp
        super().__init__(transactions)

    @property
    def _generate_frames(self):
        # initialization
        selected = set(((),))

        frames = {
            'Start': {
                **{
                    f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, (), ())
                    for i1 in self.itemsets
                    for i2 in self.itemsets
                },
                **{
                    f'node_{self._name(i1)}': {
                        'backgroundColor': self._node_color(i1, (), (), (), selected),
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

        # transform transactions
        all_items = {}

        for tid, itemset in self.transactions:
            for item in itemset:
                if (item,) not in all_items:
                    all_items[(item,)] = OrderedSet()

                all_items[(item,)].add(tid)

        # call bottom up algorithm
        for name, frame in self.bottom_up(all_items, self.min_supp, selected):
            frames[name] = frame

        # end
        frames['Ende des Algorithmus'] = {
            **{
                f'node_{self._name(i1)}': {
                    'backgroundColor': self._node_color(i1, [], [], [], selected),
                    'color': 'whitesmoke'
                }
                for i1 in self.itemsets
            },
        }

        return frames

    def bottom_up(self, items, min_supp, selected: Set, parents=((),)):
        # Abbrechen, falls keine Items mehr verbleiben.
        if not items:
            return

        yield f'Generieren (Knoten: {tuple(items.keys())})', {
            **{
                f'node_{self._name(i1)}': {
                    'backgroundColor': self._node_color(i1, tuple(items.keys()), parents, [], selected),
                    'color': 'whitesmoke'
                }
                for i1 in self.itemsets
            },
            **{
                f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, parents, tuple(items.keys()))
                for i1 in self.itemsets
                for i2 in self.itemsets
            },
        }

        # Items nach minimalem Support filtern.
        filtered_items = {k: v
                          for k, v in items.items()
                          if len(v) >= min_supp}

        selected.update(filtered_items)
        removed_items = [k for k, v in items.items() if len(v) < min_supp]

        # Alle verbleibenden Itemsets zurückgeben, da sie
        # bereits den minimalen Support-Wert erfüllen.
        yield f'Filtern (Eltern: {parents}, Knoten: {tuple(items.keys())})', {
            **{
                f'node_{self._name(i1)}': {
                    # 'backgroundColor': self._node_color(i1, filtered_items.keys(), (), removed_items, selected),
                    'backgroundColor': self._node_color(i1, (), (), removed_items, selected),
                    'color': 'whitesmoke'
                }
                for i1 in self.itemsets
            },
            **{
                f'edge_{self._name(i1)}_{self._name(i2)}': self._edge_style(i1, i2, (), ())
                for i1 in self.itemsets
                for i2 in self.itemsets
            },
        }

        # Über alle verbleibenden Items iterieren.
        for item1, item1_tids in filtered_items.items():
            # Neues Dictionary für neues Präfix erstellen.
            new_items = {}

            # Über alle verbleibenden Items iterieren, um
            # Paare zu bilden.
            for item2, item2_tids in filtered_items.items():
                # Überspringen, falls Paar nicht geordnet ist,
                # um doppelte Behandlung zu vermeiden.
                if item1 >= item2:
                    continue

                # Paarung hinsichtlich des Präfix überprüfen.
                # Überspringen, falls Präfix nicht übereinstimmt.
                prefix_len = len(item1) - 1
                if item1[:prefix_len] != item2[:prefix_len]:
                    continue

                # Neuen Eintrag anhand der zusammengesetzten
                # Itemsets bilden. Die gemeinsamen Transaktionen
                # werden durch einen Schnitt gefunden.
                new_items[item1 + item2[prefix_len:]] = item1_tids & item2_tids

            # Rekursiver Aufruf mit gefundenen Kandidaten.
            yield from self.bottom_up(new_items, min_supp, selected, parents=tuple(filtered_items.keys()))

    @staticmethod
    def _node_color(i1, active, parents, removed, selected):
        if i1 in active:
            return f'rgb({colors[2]})'
        if i1 in parents:
            return f'rgb({color_secondary}'
        if i1 in removed:
            return f'rgb({color_error})'
        if i1 in selected:
            return f'rgb({color_primary})'
        else:
            return '#AAAAAA'

    @staticmethod
    def _edge_style(i1, i2, parents, items):
        if i1 in parents and i2 in items:
            return {
                'backgroundColor': f'rgba({colors[2]}, 0.67)',
                'size': 2
            }
        else:
            return {
                'backgroundColor': 'rgba(0, 0, 0, 0.67)',
                'size': 1
            }
