from typing import List, Tuple

from .FPTree import FPTree


class ConditionalFPTree(FPTree):
    def __init__(self, original_fp_tree, cpt: List[Tuple[int, List[str]]], itemset: str):
        self.cpt: List[Tuple[int, List[str]]] = cpt
        # count 1-itemsets
        itemsets = {}

        for count, items in cpt:
            for item in items:
                itemsets[item] = itemsets.get(item, 0) + count

        # build transactions
        transactions = []

        tid = 0
        for count, items in cpt:
            for _ in range(count):
                tid += 1
                transactions.append((
                    tid,
                    tuple(i for i in items if itemsets[i] >= original_fp_tree.min_supp)
                    # Itemset(*items).filter(lambda x: itemsets[x] >= original_fp_tree.min_supp)
                ))

        # initialize super class
        super().__init__(transactions, original_fp_tree.min_supp, head_name=itemset, sort=False)

    def _generate_frames(self):
        counts = {}
        for count, items in self.cpt:
            for item in items:
                counts[item] = counts.get(item, 0) + count

        fp_tree = {}
        header_table = {}

        unlocked_nodes = {''}

        for count, items in self.cpt:
            current_transaction = f'{"".join(items)}:{count}'

            frame = {
                'current_transaction': f'Aktuelle Musterbasis: {current_transaction}',
                **{
                    f'node_{node}': {
                        'backgroundColor': '#636EFA',
                        'color': 'whitesmoke'
                    }
                    for node in unlocked_nodes
                }
            }

            frame['node_'] = {
                'backgroundColor': '#EF553B',
                'color': 'whitesmoke'
            }

            relevant_items = tuple(i for i in items if counts[i] >= self.min_supp)
            frame['cleaned_transaction'] = 'Bereinigt: {' + ', '.join(relevant_items) + '}'

            node = fp_tree
            previous_unique_name_str = ''

            for d, element in enumerate(relevant_items, start=1):
                unique_name = relevant_items[:d]
                unique_name_str = ''.join(unique_name)

                if unique_name not in node:
                    node[unique_name] = [0, {}]

                    if element not in header_table:
                        header_table[element] = []
                    header_table[element].append(node[unique_name])

                node[unique_name][0] += count

                frame[f'name_{unique_name_str}'] = f'{unique_name[-1]} ({node[unique_name][0]})'

                frame[f'node_{unique_name_str}'] = {
                    'backgroundColor': '#EF553B',
                    'color': 'whitesmoke'
                }

                frame[f'edge_{previous_unique_name_str}_{unique_name_str}'] = {
                    'backgroundColor': 'rgba(99, 110, 250, 0.5)'
                }

                unlocked_nodes.add(unique_name_str)
                node = node[unique_name][1]
                previous_unique_name_str = unique_name_str

            header_dict = {}
            for key in header_table:
                if key not in header_dict:
                    header_dict[key] = []

                for a, _ in header_table[key]:
                    header_dict[key].append(a)

            for fi in self.frequent_items:
                if fi not in header_dict:
                    continue

                frame[f'{fi}_text'] = ', '.join(f'{fi} ({e})' for e in header_dict[fi])
                frame[f'{fi}_frequency'] = sum(header_dict[fi])

            yield current_transaction, frame

        yield 'Ende der Musterbasen', {
            'current_transaction': '',
            'cleaned_transaction': '',
            **{
                f'node_{node}': {
                    'backgroundColor': '#636EFA',
                    'color': 'whitesmoke'
                }
                for node in unlocked_nodes
            }
        }
