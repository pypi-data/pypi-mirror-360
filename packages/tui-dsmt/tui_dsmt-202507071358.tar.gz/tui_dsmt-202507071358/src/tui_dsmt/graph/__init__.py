from .BFS import BFS
from .BipartiteFlow import BipartiteFlow
from .BronKerbosch import BronKerbosch
from .DFS import DFS
from .Dijkstra import Dijkstra
from .EdmondsKarp import EdmondsKarp
from .FordFulkerson import FordFulkerson
from .FruchtermanReingold import FruchtermanReingold
from .GirvanNewman import GirvanNewman
from .Hall import Hall
from .InteractiveGraph import InteractiveGraph
from .Kruskal import Kruskal
from .LabelPropagation import LabelPropagation
from .MaximumFlow import MaximumFlow
from .RandomWalk import RandomWalk
from .StoerWagner import StoerWagner
from .game import guess_adj_list, guess_adj_matrix
from .representation import draw_adj_list, draw_adj_matrix


def set_label(c):
    s = ','.join(map(str, c))
    return f'{{{s}}}'
