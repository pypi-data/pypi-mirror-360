from typing import Dict

import networkx as nx
import plotly.graph_objects as go


class InteractiveGraph:
    @staticmethod
    def __new__(cls, graph: nx.Graph, pos: Dict, importance: Dict = None):
        # nodes
        node_x = []
        node_y = []

        node_text = []

        if importance is None:
            node_color = '#636EFA'
            color_bar = None
        else:
            node_color = []
            color_bar = dict(
                thickness=15,
                xanchor='left',
                # titleside='right'
            )

        for node in graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            if importance is None:
                node_text.append(node)
            else:
                node_text.append(f'{node} ({importance[node]})')
                node_color.append(importance[node])

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            text=node_text,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                colorscale='inferno',
                colorbar=color_bar,
                color=node_color
            )
        )

        # edges
        edge_x = []
        edge_y = []

        for u, v in graph.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend((x0, x1, None))
            edge_y.extend((y0, y1, None))

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(
                width=0.5,
                color='#AAAAAA'
            ),
            hoverinfo='none',
            mode='lines'
        )

        return go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                height=700,
                margin=dict(b=0, l=0, r=0, t=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
