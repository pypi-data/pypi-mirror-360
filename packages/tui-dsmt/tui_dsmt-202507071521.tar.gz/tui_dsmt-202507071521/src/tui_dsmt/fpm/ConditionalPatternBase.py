from typing import Dict

from .ConditionalFPTree import ConditionalFPTree
from .FPTree import FPTree
from ..jpanim import JupyterAnimation


# Das rumgepatche am Namen mit [::-1] fällt mir noch auf die Füße...
class ConditionalPatternBase(JupyterAnimation):
    def __init__(self, fp_tree: FPTree, prefix: str = ''):
        self._fp_tree: FPTree = fp_tree
        self._prefix: str = prefix

        # generate some required values
        names = {key: value for key, value in self._tree_to_names(fp_tree.fp_tree)}

        links = {}
        for key, value in names.items():
            k = key[-1]

            if k not in links:
                links[k] = []
            links[k].append(value)

        # header table
        header_table_html = ''
        for fi in fp_tree.frequent_items:
            header_table_html += f'''
                <tr>
                    <td>{fi}</td>
                    <td>{{{{frame.{fi}_text}}}}</td>
                    <td>{{{{frame.{fi}_cpb}}}}</td>
                </tr>     
            '''

        # frame initialization
        def edge_color(u, v):
            if len(u) == 0 or len(v) == 0 or u[-1] != v[-1]:
                return 'rgba(99, 110, 250, 0.5)'
            else:
                return 'transparent'

        frames = {
            'Ende der Transaktionen': {
                **{
                    f'name_{node}': f'{node[-1]} ({names[node]})' if len(node) > 0 else (
                        fp_tree.head_name[::-1] if fp_tree.head_name not in ('{}', '}{') else '{}'
                    )
                    for node in fp_tree.graph.nodes
                },
                **{
                    f'node_{node}': {
                        'backgroundColor': '#636EFA',
                        'color': 'whitesmoke'
                    }
                    for node in fp_tree.graph.nodes
                },
                **{
                    f'edge_{u}_{v}': {
                        'backgroundColor': edge_color(u, v)
                    }
                    for u, v in fp_tree.graph.edges
                },
                **{
                    f'{fi}_text': ', '.join(f'{fi} ({v})' for v in links[fi])
                    for fi in fp_tree.frequent_items
                },
                **{
                    f'{fi}_cpb': ''
                    for fi in fp_tree.frequent_items
                }
            }
        }

        # frame generation
        self.cpb = {}

        for fi in fp_tree.frequent_items:
            cpb_fi = self._prefix + fi
            self.cpb[cpb_fi] = []

            for count, key in self._find_references(fp_tree.fp_tree, fi):
                prefix_key = key[:-1]
                self.cpb[cpb_fi].append((count, prefix_key))

                prefix = ''.join(prefix_key)
                value = ' '.join(f'{"".join(k)}:{c}' for c, k in self.cpb[cpb_fi])

                prefix_nodes = set(''.join(key[:i]) for i in range(0, len(key)))
                main_node = ''.join(key)

                def color(node):
                    if node in prefix_nodes:
                        return '#FFA15A'
                    if node == main_node:
                        return '#EF553B'
                    else:
                        return '#636EFA'

                frames[f'{fi} ({count}) mit Präfix {self._prefix}{prefix}'] = {
                    f'{fi}_cpb': value,
                    **{
                        f'node_{node}': {
                            'backgroundColor': color(node),
                            'color': 'whitesmoke'
                        }
                        for node in fp_tree.graph.nodes
                    }
                }

        frames['Ende der konditionalen Musterbasis'] = {
            f'node_{node}': {
                'backgroundColor': '#636EFA',
                'color': 'whitesmoke'
            }
            for node in fp_tree.graph.nodes
        }

        # call super
        super().__init__(
            f'''
                <div class="split">
                    {fp_tree.graph_html}
                    
                    <div style="padding: 1rem">
                        <table class="fp_tree_header_table">
                            <tr>
                                <th>Itemset</th>
                                <th>Knoten im FP-Tree</th>
                                <th>Musterbasis</th>
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
                fp_tree.graph_css,
                fp_tree.layout_css
            ]
        )

    def conditional_fp_tree(self, itemset):
        new_prefix = self._prefix + itemset
        return ConditionalFPTree(self._fp_tree, self.cpb[new_prefix], new_prefix)

    @staticmethod
    def _tree_to_names(fp_tree: Dict):
        if len(fp_tree) == 0:
            return

        for key, (value, children) in fp_tree.items():
            yield ''.join(key), value
            yield from ConditionalPatternBase._tree_to_names(children)

    @staticmethod
    def _find_references(fp_tree: Dict, item):
        if len(fp_tree) == 0:
            return

        for key, (value, children) in fp_tree.items():
            # if item == key[-1]:
            if item == key[-1] and len(key) > 1:
                yield value, key

            yield from ConditionalPatternBase._find_references(children, item)
