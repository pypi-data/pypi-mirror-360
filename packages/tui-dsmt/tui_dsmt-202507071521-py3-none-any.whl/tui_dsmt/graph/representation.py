from typing import Dict, List

import networkx as nx


def draw_adj_list(adj_list: Dict[str, List[str]]):
    graph = nx.DiGraph()
    for source, adj in adj_list.items():
        graph.add_node(source)
        for target in adj:
            graph.add_edge(source, target)

    return nx.draw_spring(graph, with_labels=True, font_color='whitesmoke')


def draw_adj_matrix(nodes: List[str], adj_matrix: List[List[int]]):
    assert len(nodes) == len(adj_matrix)
    assert all(len(nodes) == len(adj) for adj in adj_matrix)

    graph = nx.DiGraph()

    for n in nodes:
        graph.add_node(n)

    for source, adj in zip(nodes, adj_matrix):
        for target, value in zip(nodes, adj):
            assert value in (0, 1)
            if value:
                graph.add_edge(source, target)

    return nx.draw_spring(graph, with_labels=True, font_color='whitesmoke')
