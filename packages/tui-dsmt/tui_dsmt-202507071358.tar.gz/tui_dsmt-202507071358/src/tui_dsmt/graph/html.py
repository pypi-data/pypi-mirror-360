from typing import Dict, Tuple, Union
from uuid import uuid4

import networkx as nx

from ..util import unique_name


def _split_measure(value: str):
    digits = [c for c in value if not c.isalpha()]
    letters = [c for c in value if c.isalpha()]

    return float(''.join(digits)), ''.join(letters)


def _scale_measure(attr: str, value: str, scale: float = 2.0, offset: float = 0.3):
    num, unit = _split_measure(value)
    return f'`${{{num} / ({attr}.size * {scale}) + {offset}}}{unit}`'


def graph_to_html(graph: nx.Graph, layout: Dict,
                  weights: str = None,
                  display_height: str = '40rem', max_width: str = '100%',
                  node_width: str = '10rem', node_height: str = '2rem',
                  animated_positions: bool = False,
                  return_wrapper_id: bool = False) -> Union[Tuple[str, str], Tuple[str, str, str]]:
    nodes = list(graph.nodes)
    adj = nx.to_numpy_array(graph)

    min_x, max_x, min_y, max_y = None, None, None, None
    for (px, py) in layout.values():
        if min_x is None or px < min_x:
            min_x = px
        if max_x is None or px > max_x:
            max_x = px
        if min_y is None or py < min_y:
            min_y = py
        if max_y is None or py > max_y:
            max_y = py

    nodes_html = []
    nodes_positions = {}

    for key, (px, py) in layout.items():
        if max_x == min_x:
            left = 50
        else:
            left = (px - min_x) / (max_x - min_x) * 100 if min_x < max_x else 50

        if max_y == min_y:
            top = 0
        else:
            top = (py - min_y) / (max_y - min_y) * 100

        nodes_html.append(f'''
            <div class="node"
                 style="left: calc({left}% - {node_width} / 2); top: calc({top}% - {node_height} / 2)"
                 :style="frame.node_{key}"
                 v-html="frame.name_{key}">
            </div>
        ''')
        nodes_positions[key] = (left, top)

    lines_svg_defs = []
    lines_svg = []

    for row_i, (row, source_node) in enumerate(zip(adj, nodes)):
        source_node_esc = source_node if not isinstance(source_node, str) else source_node.replace(',', '_')

        for col_i, (value, target_node) in enumerate(zip(row, nodes)):
            target_node_esc = target_node if not isinstance(target_node, str) else target_node.replace(',', '_')

            if value and (row_i < col_i or isinstance(graph, nx.DiGraph)):
                id = unique_name()
                x1, y1 = nodes_positions[source_node_esc]
                x2, y2 = nodes_positions[target_node_esc]

                if x2 < x1:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                    arrow = 'marker-start'
                    orient = 'auto-start-reverse'
                else:
                    arrow = 'marker-end'
                    orient = 'auto'

                attr = f'frame.edge_{source_node_esc}_{target_node_esc}'

                if isinstance(graph, nx.DiGraph):
                    marker_id = unique_name()

                    lines_svg_defs.append(f'''
                        <marker id="head-{marker_id}" orient="{orient}"
                                v-bind="{{ 'refX': {_scale_measure(attr, node_width)} }}" refY="5"
                                markerHeight="40" markerWidth="50">
                            <path :fill="{attr}.backgroundColor" d="M0,0 V10 L5,5 Z" />
                        </marker>
                    ''')
                    lines_svg.append(f'''
                        <line id="{id}" 
                              x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%"
                              :stroke-width="{attr}.size ?? 2" :stroke="{attr}.backgroundColor"
                              {arrow}="url(#head-{marker_id})" />
                    ''')
                else:
                    if animated_positions:
                        lines_svg.append(f'''
                            <line id="{id}" 
                                  :x1="frame.edge_{source_node_esc}_{target_node_esc}.x1" :y1="frame.edge_{source_node_esc}_{target_node_esc}.y1" :x2="frame.edge_{source_node_esc}_{target_node_esc}.x2" :y2="frame.edge_{source_node_esc}_{target_node_esc}.y2"
                                  :stroke-width="{attr}.size ?? 2" :stroke="{attr}.backgroundColor"
                                  :stroke-dasharray="{attr}.dash" />
                        ''')
                    else:
                        lines_svg.append(f'''
                            <line id="{id}" 
                                  x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%"
                                  :stroke-width="{attr}.size ?? 2" :stroke="{attr}.backgroundColor"
                                  :stroke-dasharray="{attr}.dash" />
                        ''')

                if weights is not None:
                    weight = graph.get_edge_data(source_node, target_node)[weights]
                else:
                    weight = f'{{{{{attr}.text}}}}'

                lines_svg.append(f'''
                    <text font-size="10" :fill="{attr}.color">
                        <textPath href="#{id}" startOffset="50%" text-anchor="middle">
                            <tspan dy="-5">{weight}</tspan>
                        </textPath>
                    </text>
                ''')

    nodes_html_str = '\n'.join(nodes_html)
    lines_svg_devs_str = '\n'.join(lines_svg_defs)
    lines_svg_str = '\n'.join(lines_svg)

    lines_svg_str += '<textPath path="M0%,0% L20%,20%">?</textPath>'

    wrapper_id = f'wrapper_{unique_name()}'
    html = f'''
        <div class="node-wrapper" id="{wrapper_id}">
            <div class="node-container">
                <svg style="overflow: visible">
                    <defs>
                        {lines_svg_devs_str}
                    </defs>

                    {lines_svg_str}
                </svg>
    
                {nodes_html_str}
            </div>
        </div>
    '''
    css = f'''
        #{wrapper_id} {{
            padding: calc({node_height} / 2) calc({node_width} / 2);
            box-sizing: border-box;
            overflow-y: hidden;
        }}
    
        #{wrapper_id} .node-container {{
            width: 100%;
            max-width: {max_width};
            height: {display_height};
            position: relative;
        }}

        #{wrapper_id} .node-container svg {{
            width: 100%;
            height: {display_height};
        }}

        #{wrapper_id} .node-container .node {{
            position: absolute;
            width: {node_width};
            height: {node_height};
            background-color: red;
            
            display: flex;
            justify-content: center;
            align-items: center;
            
            text-align: center;

            border-radius: calc({node_height} / 2);
        }}
    '''

    if not return_wrapper_id:
        return html, css
    else:
        return html, css, wrapper_id
