import json
import os
from typing import Tuple, Dict

import networkx as nx

# location of this file is required to load resource urls
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# Pregel
def load_pregel_sp() -> Tuple[nx.DiGraph, Dict]:
    graph_path = os.path.join(__location__, 'resources', 'pregel_sp.csv')
    graph = nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',')

    pos_path = os.path.join(__location__, 'resources', 'pregel_sp_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)

    return graph, pos


def load_pregel_pagerank() -> Tuple[nx.DiGraph, Dict]:
    graph_path = os.path.join(__location__, 'resources', 'pregel_pagerank.csv')
    graph = nx.read_edgelist(graph_path, create_using=nx.DiGraph, delimiter=',')

    pos_path = os.path.join(__location__, 'resources', 'pregel_pagerank_pos.json')
    with open(pos_path, 'r') as f:
        pos = json.load(f)

    return graph, pos


# MapReduce
text_filenames = [
    f'{name}.txt'
    for name in (
        'faust1', 'faust2', 'kabale', 'kaufmann', 'prometheus', 'raeuber', 'romeo'
    )
]

text_paths = [
    os.path.join(__location__, 'resources', filename)
    for filename in text_filenames
]


def load_texts() -> Dict[str, str]:
    def load(path: str) -> str:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()

    return {
        filename: load(path)
        for filename, path in zip(text_filenames, text_paths)
    }
