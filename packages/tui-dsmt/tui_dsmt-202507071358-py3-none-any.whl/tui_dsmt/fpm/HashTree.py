import json
from itertools import combinations
from typing import List, Callable, Tuple, Dict, Any, Iterator

from .. import color_primary, color_secondary, color_error
from ..jpanim import JupyterAnimation
from ..util import unique_name


class HashNode:
    def __init__(self):
        self.name: str = f'n_{unique_name()}'
        self.visited: bool = False

    @property
    def max_depth(self):
        return 0

    def insert(self, values: Tuple, d: int = 0) -> Iterator:
        raise NotImplementedError

    def __str__(self, d: int = 0) -> str:
        raise NotImplementedError

    def traverse(self, key=None, parent=None, depth: int = 0) -> Iterator[Tuple['HashNode', Any, 'HashNode', int]]:
        yield self, key, parent, depth

    def apply(self, fun: Callable[['HashNode'], None]):
        for node, *_ in self.traverse():
            fun(node)


class HashInner(HashNode):
    def __init__(self, hash_function: Callable, hash_outputs: int, table_size: int):
        super().__init__()

        self.hash_function: Callable = hash_function
        self.hash_outputs: int = hash_outputs
        self.table_size: int = table_size

        self.children: Dict[Any, HashNode] = {
            i: HashLeaf(table_size)
            for i in range(hash_outputs)
        }

    @property
    def max_depth(self):
        return max(c.max_depth for c in self.children.values()) + 1

    def insert(self, values: Tuple, d: int = 0, retry: bool = False) -> Iterator:
        hashed = self.hash_function(values[d])

        if not retry:
            yield f'Hash {d + 1}: {values[d]} -> {hashed} (Itemset: {values})', {
                **{
                    f'{self.name}_{i}_bg': f'rgb({color_primary})' if i == hashed else 'white'
                    for i in range(self.hash_outputs)
                },
                **{
                    f'item_{i}_bg': f'rgb({color_primary})' if i == d else 'transparent'
                    for i in range(self.hash_outputs)
                }
            }

        # Try to insert the itemset.
        try:
            yield from self.children[hashed].insert(values, d + 1)

        # IndexError occurs if the leaf is full.
        # In this case, we replace the leaf with
        # an inner node, copy the leaf's itemsets
        # and finally try to insert the current
        # itemset again.
        except IndexError as e:
            if retry:
                raise e

            old_leaf = self.children[hashed]
            new_inner = HashInner(self.hash_function, self.hash_outputs, self.table_size)

            yield f'Volles Blatt (Itemset: {values})', {
                f'{old_leaf.name}_bg': f'rgb({color_error})'
            }

            new_inner.name = old_leaf.name
            self.children[hashed] = new_inner

            for el in old_leaf.table:
                for _ in self.insert(el, d):
                    pass

            yield f'Aufteilen des Blattes (Itemset: {values})', {
                f'{old_leaf.name}_leaf': False,
                f'{new_inner.name}_inner': True,
                **{
                    f'{new_inner.name}_{i}_bg': f'rgb({color_secondary})'
                    for i in range(self.hash_outputs)
                },
                **{
                    f'{c.name}_leaf': True
                    for c in new_inner.children.values()
                },
                **{
                    f'{c.name}_text': '<br>'.join(f'({", ".join(map(str, t))})' for t in c.table)
                    for c in new_inner.children.values()
                },
                **{
                    f'line_{new_inner.name}_{i}_{c.name}_stroke': 'black'
                    for i, c in new_inner.children.items()
                }
            }

            yield from self.insert(values, d, retry=True)

    def __str__(self, d: int = 0) -> str:
        return ('\n' * min(1, d)) + '\n'.join(
            f'{" " * d}{key}: {child.__str__(d + 4)}'
            for key, child in self.children.items()
        )

    def traverse(self, key=None, parent=None, depth: int = 0) -> Iterator[Tuple['HashNode', Any, 'HashNode', int]]:
        yield from super().traverse(key, parent, depth)
        for key, child in self.children.items():
            yield from child.traverse(key, self, depth + 1)


class HashLeaf(HashNode):
    def __init__(self, table_size: int):
        super().__init__()

        self.table_size: int = table_size
        self.table: List = []

    def insert(self, values: Tuple, d: int = 0) -> Iterator:
        if len(self.table) == self.table_size:
            raise IndexError
        else:
            self.table.append(values)

            yield f'Eintragen (Itemset {values})', {
                f'{self.name}_bg': f'rgb({color_secondary})',
                f'{self.name}_text': '<br>'.join(f'({", ".join(map(str, c))})' for c in self.table)
            }

    def __str__(self, d: int = 0) -> str:
        return str(self.table)


class HashTree(JupyterAnimation):
    def __init__(self, candidates: List, hash_function: Callable, hash_outputs: int, table_size: int = 3):
        self.candidates: List = candidates
        self.hash_function: Callable = hash_function
        self.hash_outputs: int = hash_outputs
        self.table_size: int = table_size

        # Calculate some basic measurements to scale boxes
        # and calculate positions.
        for c in candidates:
            base_width = len(c) * 0.5
            break
        else:
            raise AssertionError('Kandidatenmenge ist leer')

        base_height = table_size * 1.4

        # Create a hashtree to calculate node positions. Store
        # the actions happened during the creating as frames.
        self.root = HashInner(hash_function, hash_outputs, table_size)

        self._frames = {
            'Initialisierung der Wurzel': {
                f'{self.root.name}_inner': True,
                **{
                    f'{c.name}_leaf': True
                    for c in self.root.children.values()
                },
                **{
                    f'line_{self.root.name}_{i}_{c.name}_stroke': 'black'
                    for i, c in self.root.children.items()
                }
            }
        }

        for items in candidates:
            self._frames[f'Neues Itemset: {items}'] = {
                'itemset': items,
                'itemset_highlight': False,
                **{
                    f'{e.name}_bg': 'white'
                    for e, *_ in self.root.traverse()
                },
                **{
                    f'{e.name}_{i}_bg': 'white'
                    for e, *_ in self.root.traverse()
                    for i in range(hash_outputs)
                },
                **{
                    f'item_{i}_bg': 'transparent'
                    for i in range(hash_outputs)
                }
            }

            for name, frame in self.root.insert(items):
                if name in self._frames:
                    print('!', name)

                self._frames[name] = frame

        self._frames['Ende der Eintragungen'] = {
            **{
                f'{e.name}_bg': 'white'
                for e, *_ in self.root.traverse()
            },
            **{
                f'{e.name}_{i}_bg': 'white'
                for e, *_ in self.root.traverse()
                for i in range(hash_outputs)
            },
            'itemset': ''
        }

        # Actually calculate node positions to make it look
        # like a tree.
        per_level = {i: [] for i in range(self.root.max_depth + 1)}
        connections = {}

        y_step = 1.0 / self.root.max_depth
        y_pos = {}

        for el, key, parent, depth in self.root.traverse():
            y_pos[el.name] = depth * y_step
            per_level[depth].append(el)

            if parent is not None:
                if parent.name not in connections:
                    connections[parent.name] = []
                connections[parent.name].append(el.name)

        x_pos = {}

        for level in per_level.values():
            x_step = 1.0 / (len(level) + 1)

            for i, el in enumerate(level):
                x_pos[el.name] = x_step + i * x_step

        # From here HTML is created.
        # Inner nodes are the ones that contain a hash-table
        # and references to child nodes.
        inner = []

        for el, *_ in self.root.traverse():
            offset = (hash_outputs - 1) / 2

            for i in range(hash_outputs):
                style = {
                    'width': f'{base_width}rem',
                    'height': '3rem',
                    'display': 'flex',
                    'justify-content': 'center',
                    'align-items': 'center',
                    'position': 'absolute',
                    'left': f'calc({x_pos[el.name]} * 100% + {(i - offset) * base_width}rem - {0.5 * base_width}rem)',
                    'top': f'calc({y_pos[el.name]} * 100% + 1rem)',
                    'box-sizing': 'border-box',
                    'border': '1px solid black'
                }
                style_html = '; '.join(f'{k}: {v}' for k, v in style.items())

                inner.append(f'''
                    <div id="{el.name}_{i}"
                         style="{style_html}"
                         :style="{{
                             visibility: frame.{el.name}_inner ? 'visible' : 'hidden',
                             backgroundColor: frame.{el.name}_{i}_bg ? frame.{el.name}_{i}_bg : 'white'
                        }}">
                        {i}
                    </div>
                ''')

        inner_html = '\n'.join(inner)

        # Leaves contain lists of itemsets. While the algorithm
        # is running a leaf can transform into an inner node.
        # Therefore, they share the same positions and we only
        # hide or display whatever we need in the current frame.
        leaves = []

        for el, *_ in self.root.traverse():
            style = {
                'width': f'{3 * base_width}rem',
                'height': f'{base_height}rem',
                'padding': '0.2rem 0.4rem',
                'font-size': '90%',
                'position': 'absolute',
                'left': f'calc({x_pos[el.name]} * 100% - {1.5 * base_width}rem)',
                'top': f'calc({y_pos[el.name]} * 100%)',
                'box-sizing': 'border-box',
                'border': '1px solid black',
                'background-color': 'white'
            }
            style_html = '; '.join(f'{k}: {v}' for k, v in style.items())

            leaves.append(f'''
                <div id="{el.name}"
                     style="{style_html}"
                     :style="{{
                         visibility: frame.{el.name}_leaf ? 'visible' : 'hidden',
                         backgroundColor: frame.{el.name}_bg ? frame.{el.name}_bg : 'white'
                     }}"
                     v-html="frame.{el.name}_text">
                </div>
            ''')

        leaves_html = '\n'.join(leaves)

        # We use a svg graphic for lines / edges. However,
        # calculating their position using CSS is not possible.
        # First, we add them approximately and then fine-tune
        # the position when displaying them using JavaScript.
        svg = []
        lines = []

        for el, key, parent, _ in self.root.traverse():
            if parent is None:
                continue

            line_id = f'line_{parent.name}_{key}_{el.name}'
            lines.append({
                's': f'{parent.name}_{key}',
                't': f'{el.name}_{hash_outputs // 2}',
                'l': line_id
            })

            x1, y1 = x_pos[parent.name], y_pos[parent.name]
            x2, y2 = x_pos[el.name], y_pos[el.name]

            svg.append(f'''
                <line id="{line_id}"
                      x1="{x1 * 100}%" y1="{y1 * 100}%" x2="{x2 * 100}%" y2="{y2 * 100}%"
                      stroke-width="2"
                      :stroke="frame.{line_id}_stroke ? frame.{line_id}_stroke : 'transparent'" />
            ''')

        svg_html = '\n'.join(svg)

        # Finally, the HTML is constructed.
        container_id = f'container_{unique_name()}'
        svg_id = f'svg_{unique_name()}'

        html = f'''
            <div style="padding: 1rem 1rem 6rem; position: relative; box-sizing: border-box">
                <div style="position: absolute; top: 1rem; left: 1rem" 
                     :style="{{ visibility: frame.hide_legend ? 'hidden' : 'visible' }}">
                    Aktuelles Itemset:
                    <span v-for="(item, i) in frame.itemset"
                          style="padding: 0.5rem"
                          :style="{{ backgroundColor: frame[`item_${{i}}_bg`] }}">
                        {{{{item}}}}
                    </span>
                </div>
            
                <svg id="{svg_id}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: visible">
                    {svg_html}
                </svg>
                    
                <div id="{container_id}" style="width: 100%; height: 30rem; position: relative">
                    {inner_html}
                    {leaves_html}
                </div>
            </div>
        '''

        # But wait, we still need the JavaScript
        # to fine-tune the positions of the edges.
        js = [
            f'const svg = "{svg_id}"',
            f'const lines = {json.dumps(lines)}',
            '''
                function resize() {
                    for (let line of lines) {
                        const ct = document.getElementById(svg).getBoundingClientRect();
                        const cbrs = document.getElementById(line.s).getBoundingClientRect();
                        const cbrt = document.getElementById(line.t).getBoundingClientRect();
                        
                        const x1 = (cbrs.left + cbrs.right) / 2 - ct.left;
                        const y1 = cbrs.bottom - ct.top - 3;
                        const x2 = (cbrt.left + cbrt.right) / 2 - ct.left;
                        const y2 = cbrt.top - ct.top + 3;
                        
                        const lobj = document.getElementById(line.l);
                        lobj.setAttribute('x1', x1);
                        lobj.setAttribute('y1', y1);
                        lobj.setAttribute('x2', x2);
                        lobj.setAttribute('y2', y2);
                    }
                }
                
                onMounted(() => {
                    window.addEventListener("resize", resize);
                    resize();
                });
                
                onUnmounted(() => {
                    window.removeEventListener("resize", resize);
                })
            '''
        ]

        # Some styling might be required later?
        css = '''
            
        '''

        # Now call the parent's constructor to create
        # an animation from all the stuff.
        super().__init__(html, self.frames, style=css, js=js)

    @property
    def frames(self):
        return self._frames

    def find(self, transaction: Tuple):
        return HashTreeFind(self.candidates,
                            self.hash_function,
                            self.hash_outputs,
                            self.table_size,
                            transaction)


class HashTreeFind(HashTree):
    def __init__(self, candidates: List, hash_function: Callable, hash_outputs: int, table_size: int,
                 transaction: Tuple):
        self.transaction: Tuple = transaction
        super().__init__(candidates, hash_function, hash_outputs, table_size)

    @property
    def frames(self):
        # Set visited=False on all nodes.
        def reset(n):
            n.visited = False

        self.root.apply(reset)

        # Calculate start frame from all other frames.
        start_frame = {
            # 'hide_legend': True
        }

        for frame in self._frames.values():
            for key, value in frame.items():
                start_frame[key] = value

        start_frame['itemset'] = self.transaction
        for i in range(len(self.transaction)):
            start_frame[f'item_{i}_bg'] = 'transparent'

        # Initialize frames dict.
        frames = {
            'Beginn der Suche': start_frame
        }

        # Generate frames.
        transaction_len = len(self.transaction)

        # for e in self.candidates:
        #     candidate_len = len(e)
        #     break
        # else:
        #     raise AssertionError('no suitable candidate found')

        def format_row(c):
            if c in combinations(self.transaction, len(c)):
                return f'<b>{c}</b>'
            else:
                return str(c)

        def gen(node, start_index=0, prefix=(), indices=()):
            # leaf
            if isinstance(node, HashLeaf):
                node_id = f'{node.name}'

                if node.visited:
                    yield f'Blatt ERNEUT erreicht mit Präfix {prefix}', {}, indices
                else:
                    node.visited = True
                    yield f'Blatt erreicht mit Präfix {prefix}', {
                        f'{node_id}_bg': f'rgb({color_error})',
                        f'{node.name}_text': '<br>'.join(map(format_row, node.table))
                    }, indices

            # inner
            else:
                if start_index < transaction_len:
                    for i in range(start_index, transaction_len):
                        value = self.transaction[i]
                        hashed = self.hash_function(value)

                        node_id = f'{node.name}_{hashed}'
                        new_prefix = prefix + (value,)
                        new_indices = indices + (i,)

                        yield f'Hash {i + 1}: {value} -> {hashed} mit Präfix {prefix}', {
                            f'{node_id}_bg': f'rgb({color_primary})',
                            **{
                                f'item_{k}_bg': (
                                    f'rgb({color_primary})' if k == i
                                    else (
                                        f'rgb({color_secondary})' if k in new_indices
                                        else 'transparent'
                                    )
                                )
                                for k in range(transaction_len)
                            }
                        }, new_indices

                        for t, frame, i in gen(node.children[hashed], i + 1, new_prefix, new_indices):
                            frame[f'{node_id}_bg'] = f'rgb({color_secondary})'
                            yield t, frame, i

                else:
                    yield 'Ende der Suche', {
                        f'item_{i}_bg': 'transparent'
                        for i in range(len(self.transaction))
                    }, indices

        for title, frame, indices in gen(self.root):
            if title in frames:
                print('!', title)

            frames[title] = frame

        return frames
