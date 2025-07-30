import bz2
import json
import os
import pickle
import random
import re
from typing import Tuple, Dict

import matplotlib.pyplot as plt
import networkx as nx

# location of this file is required to load resource urls
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# helper functions
def _get_path(filename: str) -> str:
    return os.path.join(__location__, 'resources', filename)


# algorithms: dach cities
def load_dach_cities() -> nx.Graph:
    graph_path = _get_path('dach_cities.csv')
    return nx.read_edgelist(graph_path, delimiter=',')


# cliques examples
def load_cliques_small() -> nx.Graph:
    graph_path = _get_path('cliques_small.csv')
    return nx.read_edgelist(graph_path, delimiter=',', nodetype=int)


# spanning tree: Thuringian forest
def load_tw_cities() -> Tuple[nx.Graph, Dict]:
    graph_path = _get_path('tw.csv')
    graph = nx.read_edgelist(graph_path, delimiter=',')

    pos_path = _get_path('tw_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)

    return graph, pos


def draw_tw_cities(G: nx.Graph, pos: Dict):
    nx.draw(G, pos=pos, node_size=100, node_color='#EEE2DE')
    nx.draw_networkx_labels(G, pos, font_size=7)

    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_size=6)

    plt.show()
    plt.close()


# maximum flow
def load_mf_ex1() -> nx.Graph:
    graph_path = _get_path('mf_ex1.csv')
    return nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',')


def load_mf_ex2() -> nx.Graph:
    graph_path = _get_path('mf_ex2.csv')
    return nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',')


# bipartite: lecture
def load_bi_flow() -> nx.DiGraph:
    graph_path = _get_path('bi_flow.csv')
    return nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',')


def load_bi_small() -> nx.Graph:
    graph_path = _get_path('bi_small.csv')
    return nx.read_edgelist(graph_path, delimiter=',')


def load_bi_recommendations() -> nx.DiGraph:
    graph_path = _get_path('bipartite_recommendations.csv')
    return nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',')


def draw_bi(G):
    nodes = [node for node in G if re.fullmatch(r'[A-Za-z]+', node)]

    pos = nx.bipartite_layout(G, nodes)
    nx.draw(G, pos, with_labels=True, font_color='whitesmoke')


# bipartite: exams
def load_exams() -> nx.DiGraph:
    graph_path = _get_path('bipartite_exams.csv')
    return nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',')


def draw_exams(graph: nx.DiGraph, source: str = 's', target: str = 't'):
    def _filter_exams_nodes(g: nx.DiGraph):
        for node in g.nodes:
            if node.startswith('G'):
                yield node

    def _sort_exams_nodes(node):
        if node.startswith('G'):
            return f'G{int(node[1:]):03}'
        if node.startswith('Mo '):
            return f'W1 {node[3:]}'
        if node.startswith('Di '):
            return f'W2 {node[3:]}'
        if node.startswith('Mi '):
            return f'W3 {node[3:]}'
        if node.startswith('Do '):
            return f'W4 {node[3:]}'
        else:
            return node

    st = source, target
    left = set(_filter_exams_nodes(graph))

    # initialize figure
    plt.figure(figsize=(8, 11))

    # layout without source and target
    copy = graph.copy()
    copy.remove_nodes_from(st)
    pos = nx.bipartite_layout(copy, left)

    # add positions for source and target
    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    dx, dy = max_x - min_x, max_y - min_y

    pos[source] = [min_x - dx / 3, max_y - dy / 2]
    pos[target] = [max_x + dx / 3, max_y - dy / 2]

    # sort other nodes
    for a in sorted(pos.keys(), key=_sort_exams_nodes):
        for b in sorted(pos.keys(), key=_sort_exams_nodes):
            if a in left and b not in left or a not in left and b in left or a in st or b in st:
                continue

            if pos[a][1] > pos[b][1]:
                pos[a], pos[b] = pos[b], pos[a]

    # draw graph
    nx.draw(graph, pos, with_labels=True, font_size=6, font_color='whitesmoke', node_size=1000)
    nx.draw_networkx_edge_labels(graph, pos, nx.get_edge_attributes(graph, 'weight'), font_size=6)

    # display image
    plt.show()
    plt.close()


# Wikipedia: IT
def load_wiki_it() -> Tuple[nx.Graph, Dict]:
    graph_path = _get_path('wiki_it.tsv')
    graph = nx.read_edgelist(graph_path, delimiter='\t')

    pos_path = _get_path('wiki_it_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)

    return graph, pos


# exercise: some Wikipedia articles
def load_dewiki_sample() -> nx.DiGraph:
    graph_path = _get_path('dewiki_sample.pickle.bz2')
    with bz2.open(graph_path, 'rb') as file:
        return pickle.load(file)


# exercise: some other Wikipedia articles (undirected)
def load_dewiki_softwarearchitektur() -> nx.Graph:
    graph_path = _get_path('dewiki_softwarearchitektur.tsv')
    return nx.read_edgelist(graph_path, delimiter='\t')


# communities
def load_community_tiny() -> nx.Graph:
    graph_path = _get_path('community_tiny.csv')
    return nx.read_edgelist(graph_path, delimiter=',', nodetype=int)


# communities
def load_community_small() -> nx.Graph:
    graph_path = _get_path('community_small.csv')
    return nx.read_edgelist(graph_path, delimiter=',', nodetype=int)


# graph partitioning examples
def load_mp_small() -> Tuple[nx.DiGraph, Dict]:
    graph_path = _get_path('multiprocessing_small.csv')
    graph = nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',', nodetype=int)

    pos_path = _get_path('multiprocessing_small_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)
        pos = {int(k): v for k, v in pos.items()}

    return graph, pos


def load_mp_small_undirected() -> Tuple[nx.Graph, Dict]:
    graph_path = _get_path('multiprocessing_small.csv')
    graph = nx.read_edgelist(graph_path, delimiter=',', nodetype=int)

    pos_path = _get_path('multiprocessing_small_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)
        pos = {int(k): v for k, v in pos.items()}

    return graph, pos


def load_mp_small_weighted() -> Tuple[nx.Graph, Dict]:
    graph_path = _get_path('multiprocessing_small.csv')
    graph = nx.read_edgelist(graph_path, delimiter=',', nodetype=int)

    random.seed(12)
    for u, v in graph.edges:
        if (u, v) in ((3, 4), (4, 3)):
            graph[u][v]['weight'] = 100
        else:
            graph[u][v]['weight'] = random.randint(1, 7)

    pos_path = _get_path('multiprocessing_small_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)
        pos = {int(k): v for k, v in pos.items()}

    return graph, pos


def load_partitioning_example() -> Tuple[nx.Graph, Dict]:
    graph_path = _get_path('partitioning_example.csv')
    graph = nx.read_edgelist(graph_path, delimiter=',', nodetype=int)

    pos_path = _get_path('partitioning_example_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)
        pos = {int(k): v for k, v in pos.items()}

    return graph, pos
