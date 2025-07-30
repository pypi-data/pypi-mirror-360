from typing import Dict, Callable, Any, List, Tuple, Optional

import networkx as nx

from .. import color_primary, colors
from ..graph.html import graph_to_html
from ..jpanim import JupyterAnimation


class Pregel(JupyterAnimation):
    def __init__(self, graph: nx.DiGraph,
                 node_init: Callable[[Any], Any],
                 pregel_fun: Callable[[Any, List[Any], List[Any], Dict], Tuple[Any, bool]],
                 pos: Dict = None, node_value_key: str = 'value',
                 partition_hash_fun: Callable[[Any], int] = None,
                 print_messages: bool = False):
        self.graph: nx.DiGraph = graph
        self.partition_hash_fun: Optional[Callable[[Any], int]] = partition_hash_fun

        self.node_value_key: str = node_value_key

        # generate html
        pos = pos or nx.spring_layout(graph)
        html, css = graph_to_html(graph, pos, display_height='24rem', node_width='6rem', node_height='6rem')

        # set all nodes to active
        nx.set_node_attributes(graph, {
            n: True
            for n in graph.nodes
        }, 'active')

        # prepare frames
        frames = {
            # 'Initialisierung': {
            #     **{
            #         f'name_{n}': f'-{n}-<br>{nx.get_node_attributes(graph, node_value_key)[n]}'
            #         for n in graph.nodes
            #     },
            #     **{
            #         f'node_{n}': self.node_style(n)
            #         for n in graph.nodes
            #     },
            #     **{
            #         f'edge_{u}_{v}': self.edge_style('')
            #         for u, v in graph.edges
            #     }
            # }
        }

        # initial superstep
        messages = {}

        for node in graph.nodes:
            node_value = node_init(node)
            graph.nodes[node][node_value_key] = node_value

            for neighbor in nx.neighbors(graph, node):
                if neighbor not in messages:
                    messages[neighbor] = []

                messages[neighbor].append((node, node_value))

        frames[f'Superstep 0: Initialisierung'] = {
            **{
                f'name_{n}': self.node_name(n)
                for n in graph.nodes
            },
            **{
                f'node_{n}': self.node_style(n)
                for n in graph.nodes
            },
            **{
                f'edge_{u}_{v}': self.edge_style('')
                for u, v in graph.edges
            }
        }

        frame_messages = {
            u: {
                v: value
                for v, value in messages[u]
            }
            for u in messages
        }

        if print_messages:
            print(f'-- Superstep 0 --')

            for msg in sorted(f'{v} -> {u}: {msg}'
                              for u, msgs in frame_messages.items()
                              for v, msg in frame_messages[u].items()):
                print(msg)

            print()

        frames[f'Superstep 0: Kommunikation'] = {
            **{
                f'name_{n}': self.node_name(n)
                for n in graph.nodes
            },
            **{
                f'node_{n}': self.node_style(n)
                for n in graph.nodes
            },
            **{
                f'edge_{u}_{v}': self.edge_style(frame_messages[v][u] if v in frame_messages and u in frame_messages[v] else '')
                for u, v in graph.edges
            }
        }

        # normal supersteps
        i = 1
        local_storage = {node: {} for node in graph.nodes}

        # for node in graph.nodes:
        #     messages[node] = [(None, graph.nodes[node][node_value_key])]
        #     graph.nodes[node][node_value_key] = node_init

        while any(nx.get_node_attributes(graph, 'active').values()):
            # execute pregel function on each node
            new_messages = {}

            for node in graph.nodes:
                received_from = [f for f, _ in messages.get(node, [])]
                received_values = [v for _, v in messages.get(node, [])]

                node_value = graph.nodes[node][node_value_key]
                node_value, node_active = pregel_fun(node_value, received_from, received_values, local_storage[node])

                graph.nodes[node][node_value_key] = node_value
                graph.nodes[node]['active'] = node_active

                if node_active:
                    for neighbor in nx.neighbors(graph, node):
                        if neighbor not in new_messages:
                            new_messages[neighbor] = []

                        new_messages[neighbor].append((node, node_value))

            # store messages
            messages = new_messages

            # generate calculation frame
            frames[f'Superstep {i}: Berechnung'] = {
                **{
                    f'name_{n}': self.node_name(n)
                    for n in graph.nodes
                },
                **{
                    f'node_{n}': self.node_style(n)
                    for n in graph.nodes
                },
                **{
                    f'edge_{u}_{v}': self.edge_style('')
                    for u, v in graph.edges
                }
            }

            # reactivate nodes receiving messages
            for node in messages:
                graph.nodes[node]['active'] = True

            # generate communication frame
            frame_messages = {
                u: {
                    v: value
                    for v, value in messages[u]
                }
                for u in messages
            }

            if print_messages:
                print(f'-- Superstep {i} --')

                for msg in sorted(f'{v} -> {u}: {msg}'
                                  for u, msgs in frame_messages.items()
                                  for v, msg in frame_messages[u].items()):
                    print(msg)

                print()

            frames[f'Superstep {i}: Kommunikation'] = {
                **{
                    f'name_{n}': self.node_name(n)
                    for n in graph.nodes
                },
                **{
                    f'node_{n}': self.node_style(n)
                    for n in graph.nodes
                },
                **{
                    f'edge_{u}_{v}': self.edge_style(frame_messages[v][u] if v in frame_messages and u in frame_messages[v] else '')
                    for u, v in graph.edges
                }
            }

            # break after some iterations
            # to counter bad user functions
            i += 1
            if i >= 50:
                raise AssertionError(f'bereits {i} Iterationen')

        # initialize super
        super().__init__(html, frames, css)

    def node_name(self, node):
        value = self.graph.nodes[node][self.node_value_key]
        value = self.format_value(value)

        return f'-{node}-<br>{value}'

    def node_style(self, node):
        active = nx.get_node_attributes(self.graph, 'active')[node]

        background = f'rgb({color_primary})' if active else 'gray'
        border = f'rgb({colors[self.partition_hash_fun(node)]})' if self.partition_hash_fun is not None else background

        style = {
            'backgroundColor': background,
            'color': 'whitesmoke',
            'boxShadow': f'inset 0 0 0 0.25rem {border}'
        }

        return style

    def edge_style(self, value):
        text_value = self.format_value(value)

        return {
            'backgroundColor': f'rgb({color_primary})' if value else 'black',
            'size': 2 if value else 1,
            'text': text_value
        }

    @staticmethod
    def format_value(val):
        if val is None:
            return 'None'
        if isinstance(val, dict):
            return '{}'
        if isinstance(val, tuple):
            return tuple(map(Pregel.format_value, val))
        if isinstance(val, float):
            return f'{val:.3f}'
        else:
            return val
