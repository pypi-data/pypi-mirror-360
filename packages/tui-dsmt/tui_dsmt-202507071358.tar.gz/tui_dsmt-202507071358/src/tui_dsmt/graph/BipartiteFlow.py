import re

import networkx as nx

from .FordFulkerson import FordFulkerson


class BipartiteFlow(FordFulkerson):
    def __init__(self, graph: nx.DiGraph,
                 source: str = 's', target: str = 't',
                 capacity: str = 'capacity'):
        # get positions
        graph_copy = graph.copy()
        graph_copy.remove_nodes_from(('s', 't'))

        left_nodes = sorted(node for node in graph_copy if re.fullmatch(r'[A-Za-z]+', node))
        right_nodes = sorted(node for node in graph_copy if node not in left_nodes)

        pos = nx.bipartite_layout(graph_copy, left_nodes)

        xs = [x for x, _ in pos.values()]
        ys = [y for _, y in pos.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        dx, dy = max_x - min_x, max_y - min_y

        pos['s'] = [min_x - dx / 2, max_y - dy / 2]
        pos['t'] = [max_x + dx / 2, max_y - dy / 2]

        for c in left_nodes, right_nodes:
            for a in c:
                for b in c:
                    if pos[a][1] < pos[b][1]:
                        pos[a], pos[b] = pos[b], pos[a]

        # initialize parent
        super().__init__(graph, source, target, capacity, pos)

    def final(self):
        path = [(u, v)
                for u, v in self.residual_graph.edges
                if self.residual_graph.get_edge_data(u, v)['flow'] > 0 and u not in ('s', 't') and v not in ('s', 't')]

        return 'Lösung für Zuordnungsproblem', {
            f'edge_{u}_{v}': self.edge_style(u, v, path)
            for u, v in self.graph.edges
        }
