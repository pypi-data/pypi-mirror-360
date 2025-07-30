from typing import List, Tuple, Dict, Union, Iterator, Any

import networkx as nx

from .Itemset import Itemset
from ..graph.html import graph_to_html
from ..jpanim import JupyterAnimation
from .. import color_secondary

TRANSACTION_LIST = List[Tuple[int, Union[Itemset, Tuple]]]


# Das rumgepatche am Namen mit [::-1] fällt mir noch auf die Füße...
# z.B. #74
class FPTree(JupyterAnimation):
    def __init__(self, transactions: TRANSACTION_LIST, min_supp: int, head_name: str = '{}', sort: bool = True,
                 custom_item_order: Iterator = None):
        self.transactions: TRANSACTION_LIST = transactions
        self.min_supp: int = min_supp
        self.head_name: str = head_name

        if custom_item_order is None:
            self.custom_item_order: Dict[Any, int] = {}
        else:
            self.custom_item_order = {k: -i for i, k in enumerate(custom_item_order)}

        self.fp_tree, self.frequent_items = self._fp_tree(transactions, min_supp, sort)

        # build a graph layout
        if len(self.fp_tree) == 0:
            # raise AssertionError('FPTree is empty')
            self.graph = nx.Graph()
            self.graph.add_node('')
        else:
            self.graph = self._fp_tree_to_graph(self.fp_tree)

        pos = {''.join(key): (x, y) for key, x, y in self._fp_tree_to_pos(self.fp_tree)}
        pos[''] = (0.5, 0)

        # convert to html
        self.graph_html, self.graph_css = graph_to_html(self.graph, pos,
                                                        display_height='15rem',
                                                        node_width='4rem', node_height='2rem')

        # header table
        header_table_html = ''
        for fi in self.frequent_items:
            header_table_html += f'''
                <tr>
                    <td>{fi}</td>
                    <td>{{{{frame.{fi}_frequency}}}}</td>
                    <td>{{{{frame.{fi}_text}}}}</td>
                </tr>     
            '''

        # frame generation
        frames = {
            'Initialisierung': {
                'current_transaction': '',
                'cleaned_transaction': '',
                **{
                    f'name_{node}': node[-1] if len(node) > 0 else (head_name[::-1] if head_name != '{}' else '{}')
                    for node in self.graph.nodes
                },
                **{
                    f'node_{node}': {
                        'backgroundColor': '#636EFA',
                        'color': 'whitesmoke',
                        'display': 'none' if node != '' else 'flex'
                    }
                    for node in self.graph.nodes
                },
                **{
                    f'edge_{u}_{v}': {
                        'backgroundColor': 'transparent'
                    }
                    for u, v in self.graph.edges
                },
                **{
                    f'{fi}_frequency': 0
                    for fi in self.frequent_items
                },
                **{
                    f'{fi}_text': ''
                    for fi in self.frequent_items
                }
            }
        }

        for key, value in self._generate_frames():
            frames[key] = value

        # layout
        self.layout_css = '''
            .split {
                display: flex;
                flex-direction: row;
            }
            
            .split > div {
                width: 50%;
            }
            
            .transaction {
                height: 1.5rem;
                display: flex;
                justify-content: left;
                align-items: center;
            }
            
            .fp_tree_header_table td {
                text-align: left !important;
            }
        '''

        # call super
        super().__init__(
            f'''
                <div class="split">
                    {self.graph_html}
                    
                    <div style="padding: 1rem">
                        <table class="fp_tree_header_table">
                            <tr>
                                <th>1-Itemset</th>
                                <th>Häufigkeit</th>
                                <th>Knoten im FP-Tree</th>
                            </tr>
                            
                            {header_table_html}
                        </table>
                    </div>
                </div>
                <div class="split" style="margin-top: 1rem">
                    <div class="transaction current-transaction">
                        {{{{frame.current_transaction}}}}
                    </div>
                    <div class="transaction cleaned-transaction">
                        {{{{frame.cleaned_transaction}}}}
                    </div>
                </div>
            ''',
            frames,
            [
                self.graph_css,
                self.layout_css
            ]
        )

    @property
    def conditional_pattern_base(self):
        if self.head_name == '{}':
            prefix = ''
        else:
            prefix = self.head_name

        from .ConditionalPatternBase import ConditionalPatternBase
        return ConditionalPatternBase(self, prefix)

    def _fp_tree(self, transactions: TRANSACTION_LIST, min_supp: int, sort: bool):
        # count 1-itemsets
        counts = {}
        for _, itemset in transactions:
            for element in itemset:
                counts[element] = counts.get(element, 0) + 1

        # initialize tree and header table
        fp_tree = {}

        # iterate over itemsets
        for _, itemset in transactions:
            # filter and sort important items
            relevant_items = tuple(x for x in itemset if counts[x] >= min_supp)
            if sort:
                relevant_items = tuple(sorted(relevant_items,
                                              key=lambda x: (counts[x], self.custom_item_order.get(x, 0), x),
                                              reverse=True))

            # integrate into fp_tree
            node = fp_tree
            for d, element in enumerate(relevant_items, start=1):
                unique_name = relevant_items[:d]
                if unique_name not in node:
                    node[unique_name] = [0, {}]

                node[unique_name][0] += 1
                node = node[unique_name][1]

        # return
        frequent_itemsets = sorted((key for key, count in counts.items() if count >= min_supp),
                                   key=lambda x: (counts[x], self.custom_item_order.get(x, 0), x),
                                   reverse=True)
        return fp_tree, frequent_itemsets

    @staticmethod
    def _fp_tree_to_graph(fp_tree: Dict, graph: nx.Graph = None, recent_nodes: Dict = None):
        if len(fp_tree) == 0:
            return

        if graph is None:
            graph = nx.Graph()
            recent_nodes = {}

            for key in fp_tree:
                graph.add_edge('', ''.join(key))

        for key, (_, children) in fp_tree.items():
            parent_key = ''.join(key)
            parent_name = key[-1]

            if parent_name in recent_nodes:
                graph.add_edge(recent_nodes[parent_name], parent_key)
            recent_nodes[parent_name] = parent_key

            for child in children:
                child_key = ''.join(child)
                graph.add_edge(parent_key, child_key)

            FPTree._fp_tree_to_graph(children, graph, recent_nodes)

        return graph

    @staticmethod
    def _fp_tree_to_pos(fp_tree: Dict, y: int = 1, left: float = 0., right: float = 1.):
        if len(fp_tree) == 0:
            return

        step = (right - left) / len(fp_tree)
        offset = step / 2

        for i, (key, (_, children)) in enumerate(fp_tree.items()):
            x = left + offset + i * step
            yield key, x, y

            sub_left = left + i * step
            sub_right = left + (i + 1) * step

            yield from FPTree._fp_tree_to_pos(children, y + 1, sub_left, sub_right)

    def _generate_frames(self):
        counts = {}
        for _, itemset in self.transactions:
            for element in itemset:
                counts[element] = counts.get(element, 0) + 1

        fp_tree = {}
        header_table = {}

        recent = {}
        unlocked_nodes = {''}

        for tid, itemset in self.transactions:
            frame = {
                'current_transaction': 'Transaktion ' + str(tid) + ': {' + ', '.join(itemset) + '}',
                **{
                    f'node_{node}': {
                        'backgroundColor': '#636EFA',
                        'color': 'whitesmoke'
                    }
                    for node in unlocked_nodes
                }
            }

            relevant_items = itemset.filter(
                lambda x: counts[x] >= self.min_supp
            ).sort(
                lambda x: (counts[x], self.custom_item_order.get(x, 0), x), True
            )
            frame['cleaned_transaction'] = 'Bereinigt und sortiert: [' + ', '.join(relevant_items) + ']'

            node = fp_tree
            previous_unique_name_str = ''

            frame['node_'] = {
                'backgroundColor': '#EF553B',
                'color': 'whitesmoke'
            }

            for d, element in enumerate(relevant_items, start=1):
                unique_name = relevant_items[:d]
                unique_name_str = ''.join(unique_name)
                last_char = unique_name[-1]

                if last_char in recent:
                    recent_unique_name_str = recent[last_char]
                    for edge_name in (f'edge_{recent_unique_name_str}_{unique_name_str}',
                                      f'edge_{unique_name_str}_{recent_unique_name_str}'):
                        frame[edge_name] = {
                            'backgroundColor': f'rgba({color_secondary}, 0.67)',
                            'dash': '10,10'
                        }
                recent[last_char] = unique_name_str

                if unique_name not in node:
                    node[unique_name] = [0, {}]

                    if element not in header_table:
                        header_table[element] = []
                    header_table[element].append(node[unique_name])

                node[unique_name][0] += 1

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

            yield f'TID={tid}', frame

        yield 'Ende der Transaktionen', {
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
