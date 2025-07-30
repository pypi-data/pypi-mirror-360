import itertools
from typing import List, Tuple, Union, Optional

from .Itemset import Itemset
from ..jpanim import JupyterAnimation

TRANSACTION_LIST = List[Tuple[int, Union[Itemset, Tuple]]]


class BruteForceFI(JupyterAnimation):
    def __init__(self, transactions: TRANSACTION_LIST, min_supp: int):
        self.transactions = transactions
        self.min_supp: int = min_supp

        # store I and it's powerset
        self.I = set(y for _, x in transactions for y in x)

        self.I_powerset = {
            ''.join(i): i
            for i in itertools.chain.from_iterable(
                itertools.combinations(sorted(self.I), r)
                for r in range(1, len(self.I) + 1)
            )
        }

        # transactions
        self.all_items = []

        self.transactions_html = ''
        for tid, itemset in transactions:
            self.all_items.extend((tid, item) for item in itemset)
            itemset_str = ', '.join(f'<span :style="frame.item_{tid}_{item}">{item}</span>' for item in itemset)

            self.transactions_html += f'''
                <tr>
                    <td>{tid}</td>
                    <td>{itemset_str}</td>
                </tr>
            '''

        # itemsets
        itemsets_html = ''
        for i_id, i in self.I_powerset.items():
            i_str = ', '.join(i)

            itemsets_html += f'''
                <tr :style="frame.row_{i_id}">
                    <td :style="frame.style_{i_id}">{i_str}</td>
                    <td>{{{{ frame.count_{i_id} }}}}</td>
                </tr>
            '''

        # frames
        frames = {
            'Auflisten aller potentiellen Teilmengen': {
                **{
                    f'item_{tid}_{item}': {}
                    for tid, item in self.all_items
                },
                **{
                    f'style_{i_id}': {}
                    for i_id, i in self.I_powerset.items()
                },
                **{
                    f'count_{i_id}': 0
                    for i_id, i in self.I_powerset.items()
                },
                **{
                    f'row_{i_id}': {}
                    for i_id in self.I_powerset
                }
            }
        }

        self.counts = {i_id: 0 for i_id in self.I_powerset}

        for c_id, c in self.I_powerset.items():
            c_str = ', '.join(c)

            matching = set()
            for tid, items in transactions:
                for e in c:
                    if e not in items:
                        break
                else:
                    matching.add(tid)

            self.counts[c_id] += len(matching)

            frames[f'Teilmenge: {{{c_str}}}'] = {
                **{
                    f'item_{tid}_{item}': {
                        'color': '#EF553B' if tid in matching and item in c else 'black'
                    }
                    for tid, item in self.all_items
                },
                **{
                    f'style_{i_id}': {
                        'color': '#636EFA' if c_id == i_id else 'black'
                    }
                    for i_id in self.I_powerset
                },
                **{
                    f'count_{i_id}': self.counts[i_id]
                    for i_id in self.I_powerset
                },
                **{
                    f'row_{c_id}': {
                        'opacity': '0.4' if len(matching) < self.min_supp else '1.0'
                    }
                }
            }

        frames['Ende der Suche'] = {
            **{
                f'item_{tid}_{item}': {}
                for tid, item in self.all_items
            },
            **{
                f'style_{i_id}': {}
                for i_id in self.I_powerset
            }
        }

        # build html and initialize super
        html = f'''
            <div style="display: flex; flex-direction: row; align-items: start; justify-content: center; column-gap: 5rem">
                <table>
                    <tr>
                        <th>TID</th>
                        <th>Items</th>
                    </tr>

                    {self.transactions_html}
                </table>

                <table>
                    <tr>
                        <th>Itemset</th>
                        <th>Häufigkeit</th>
                    </tr>

                    {itemsets_html}
                </table>
            </div>
        '''

        super().__init__(html, frames)

    def association_rules(self, min_conf: float = None) -> 'BruteForceAR':
        return BruteForceAR(self, min_conf)


class BruteForceAR(JupyterAnimation):
    def __init__(self, bffi: BruteForceFI, min_conf: Optional[float]):
        self.min_conf: Optional[float] = min_conf

        self.frequent_itemsets = {i_id: (i, bffi.counts[i_id])
                                  for i_id, i in bffi.I_powerset.items()
                                  if len(i) > 1 and bffi.counts[i_id] >= bffi.min_supp}

        # prepare algorithm
        steps = {}

        for i_id, (i, _) in self.frequent_itemsets.items():
            steps[i_id] = []

            powerset = list(
                itertools.chain.from_iterable(
                    itertools.combinations(sorted(i), r)
                    for r in range(len(i) - 1, len(i))
                )
            )

            for A in powerset:
                X_A = []
                for B in i:
                    if B not in A:
                        X_A.append(B)

                steps[i_id].append((A, X_A))

        # itemsets
        itemsets_html = ''
        all_rows = []

        for i_id, (i, c) in self.frequent_itemsets.items():
            i_str = ', '.join(i)

            for v, (A, X_A) in enumerate(steps[i_id]):
                if v == 0:
                    name = i_str
                    count = c
                else:
                    name = ''
                    count = ''

                A_id = i_id + ''.join(A)
                A_str = ', '.join(A)
                X_A_id = i_id + ''.join(X_A)
                X_A_str = ', '.join(X_A)

                itemsets_html += f'''
                    <tr :style="frame.row_{i_id}_{v}">
                        <td :style="frame.style_{i_id}">{name}</td>
                        <td>{count}</td>
                        <td :style="frame.style_{A_id}_{v}">{A_str}</td>
                        <td :style="frame.style_{X_A_id}_{v}">{X_A_str}</td>
                        <td :style="frame.style_{A_id}_{X_A_id}_supp">{{{{frame.text_{A_id}_{X_A_id}_supp}}}}</td>
                        <td :style="frame.style_{A_id}_{X_A_id}_conf">{{{{frame.text_{A_id}_{X_A_id}_conf}}}}</td>
                    </tr>
                '''

                all_rows.append((v, i_id, i, i_str, A_id, A, A_str, X_A_id, X_A, X_A_str))

        # frames
        frames = {
            'Auflisten aller Teilmengen': {}
        }

        support_values = {}
        support_frames = []
        confidence_values = {}
        confidence_frames = []

        for counter, i_id, i, i_str, A_id, A, A_str, X_A_id, X_A, X_A_str in all_rows:
            common_occurrence = []
            A_occurrence = []
            X_occurrence = []

            for tid, items in bffi.transactions:
                A_check = True
                X_check = True

                for A_item in A:
                    if A_item not in items:
                        A_check = False
                        break

                for X_item in X_A:
                    if X_item not in items:
                        X_check = False
                        break

                if A_check and X_check:
                    common_occurrence.append(tid)

                if A_check:
                    A_occurrence.append(tid)

                if X_check:
                    X_occurrence.append(tid)

            # support
            support = len(common_occurrence) / len(bffi.transactions)
            support_values[(i_id, counter)] = len(common_occurrence)

            def color(tid, item):
                if tid in common_occurrence:
                    if item in A:
                        return '#636EFA'
                    if item in X_A:
                        return '#EF553B'

                return 'inherit'

            support_frames.append((f'Support von {A_str} → {X_A_str}', {
                **{
                    f'style_{B_id}_{c}': {
                        'color': '#636EFA' if B_id == A_id and c == counter else 'inherit'
                    }
                    for c, _, _, _, B_id, _, _, _, _, _ in all_rows
                },
                **{
                    f'style_{X_B_id}_{c}': {
                        'color': '#EF553B' if X_B_id == X_A_id and c == counter else 'inherit'
                    }
                    for c, _, _, _, _, _, _, X_B_id, _, _ in all_rows
                },
                **{
                    f'style_{B_id}_{X_B_id}_supp': {
                        'font-weight': 'bold' if B_id == A_id else 'inherit'
                    }
                    for _, _, _, _, B_id, _, _, X_B_id, _, _ in all_rows
                },
                f'text_{A_id}_{X_A_id}_supp': f'{support:.2f}',
                **{
                    f'style_{B_id}_{X_B_id}_conf': {
                        'font-weight': 'inherit'
                    }
                    for _, _, _, _, B_id, _, _, X_B_id, _, _ in all_rows
                },
                **{
                    f'item_{tid}_{item}': {
                        'color': color(tid, item)
                    }
                    for tid, items in bffi.transactions
                    for item in items
                }
            }))

            # confidence
            confidence = len(common_occurrence) / len(A_occurrence)
            confidence_values[(i_id, counter)] = confidence

            def color(tid, item):
                if (tid in common_occurrence or tid in A_occurrence) and item in A:
                    return '#636EFA'
                if (tid in common_occurrence) and item in X_A:
                    return '#EF553B'

                return 'inherit'

            confidence_frames.append((f'Konfidenz von {A_str} → {X_A_str}', {
                **{
                    f'style_{B_id}_{c}': {
                        'color': '#636EFA' if B_id == A_id and c == counter else 'inherit'
                    }
                    for c, _, _, _, B_id, _, _, _, _, _ in all_rows
                },
                **{
                    f'style_{X_B_id}_{c}': {
                        'color': '#EF553B' if X_B_id == X_A_id and c == counter else 'inherit'
                    }
                    for c, _, _, _, _, _, _, X_B_id, _, _ in all_rows
                },
                **{
                    f'style_{B_id}_{X_B_id}_supp': {
                        'font-weight': 'inherit'
                    }
                    for _, _, _, _, B_id, _, _, X_B_id, _, _ in all_rows
                },
                **{
                    f'style_{B_id}_{X_B_id}_conf': {
                        'font-weight': 'bold' if B_id == A_id else 'inherit'
                    }
                    for _, _, _, _, B_id, _, _, X_B_id, _, _ in all_rows
                },
                f'text_{A_id}_{X_A_id}_conf': f'{confidence:.2f}',
                **{
                    f'item_{tid}_{item}': {
                        'color': color(tid, item)
                    }
                    for tid, items in bffi.transactions
                    for item in items
                }
            }))

        for title, frame in support_frames:
            frames[title] = frame

        for title, frame in confidence_frames:
            frames[title] = frame

        # reset styles and filter
        frames['Filtern nach minimalen Support'] = {
            **{
                f'style_{A_id}_{c}': {
                    'color': 'inherit'
                }
                for c, _, _, _, A_id, _, _, _, _, _ in all_rows
            },
            **{
                f'style_{X_A_id}_{c}': {
                    'color': 'inherit'
                }
                for c, _, _, _, _, _, _, X_A_id, _, _ in all_rows
            },
            **{
                f'style_{A_id}_{X_A_id}_supp': {
                    'font-weight': 'inherit'
                }
                for _, _, _, _, A_id, _, _, X_A_id, _, _ in all_rows
            },
            **{
                f'style_{A_id}_{X_A_id}_conf': {
                    'font-weight': 'inherit'
                }
                for _, _, _, _, A_id, _, _, X_A_id, _, _ in all_rows
            },
            **{
                f'item_{tid}_{item}': {
                    'color': 'inherit'
                }
                for tid, items in bffi.transactions
                for item in items
            },
            # TODO filter using min_supp or min_conf
            **{
                f'row_{i_id}_{v}': {
                    'opacity': 1.0 if support_values[(i_id, v)] >= bffi.min_supp else 0.5
                }
                for v, i_id, _, _, _, _, _, _, _, _ in all_rows
            }
        }

        # build html and initialize super
        html = f'''
            <div style="display: flex; flex-direction: row; align-items: start; justify-content: center; column-gap: 5rem">
                <table>
                    <tr>
                        <th>TID</th>
                        <th>Items</th>
                    </tr>

                    {bffi.transactions_html}
                </table>
                
                <table>
                    <tr>
                        <th>Itemset</th>
                        <th>Häufigkeit</th>
                        <th>A</th>
                        <th>X &bsol; A</th>
                        <th>Support</th>
                        <th>Konfidenz</th>
                    </tr>
    
                    {itemsets_html}
                </table>
            </div>
        '''

        super().__init__(html, frames)
