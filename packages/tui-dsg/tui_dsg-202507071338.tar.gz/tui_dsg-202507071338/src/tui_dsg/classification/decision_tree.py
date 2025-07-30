from typing import Union, Tuple

from IPython.display import display, HTML

TREE_TYPE = Union[int, Tuple[str, 'TREE_TYPE', 'TREE_TYPE']]


def _count_levels(tree: TREE_TYPE):
    if isinstance(tree, int):
        return 1

    return max(_count_levels(tree[1]), _count_levels(tree[2])) + 1


def _draw_tree(tree: TREE_TYPE,
               left: float = 0, right: float = 1, level: int = 0,
               parent_position: float = None, parent_level: int = None):
    # get name and position
    name = tree if isinstance(tree, int) else tree[0]
    position = (left + right) / 2

    # yield name
    yield name, position, level, parent_position, parent_level

    # recursive calls
    if isinstance(tree, tuple):
        yield from _draw_tree(tree[1], left, position, level + 1, position, level)
        yield from _draw_tree(tree[2], position, right, level + 1, position, level)


def draw_dt(tree: TREE_TYPE):
    max_depth = _count_levels(tree)

    # create nodes and edges
    nodes, edges = [], []

    for name, pos, depth, parent_pos, parent_depth in _draw_tree(tree):
        # node
        type = 'inner' if isinstance(name, str) else 'leaf'
        value = 'zero' if name == 0 else 'one'

        width = 80 if type == 'inner' else 40
        top = 120 / (max_depth + 1) * (depth + 1) - 10
        left = pos * 100

        nodes.append(
            f'<div class="tree-node {type} {value}" style="top: calc({top}% - 20px); left: calc({left}% - {width / 2}px)">{name}</div>'
        )

        # edge
        if parent_pos is not None:
            parent_top = 120 / (max_depth + 1) * (parent_depth + 1) - 10
            parent_left = parent_pos * 100

            if left < parent_left:
                x1 = left
                x2 = parent_left
                o1 = 100
                o2 = 0
            else:
                x1 = parent_left
                x2 = left
                o1 = 0
                o2 = 100

            y1 = parent_top
            y2 = top

            edges.append(
                f'<svg class="tree-edge" style="left: {x1}%; top: {y1}%; width: {x2 - x1}%; height: {y2 - y1}%">'
                f'<line stroke-width="2px" stroke="#000000" x1="{o1}%" y1="0%" x2="{o2}%" y2="100%">'
                f'</svg>'
            )
            # print(max_depth, depth)

    # convert to html elements
    nodes_html = '\n'.join(nodes)
    edges_html = '\n'.join(edges)

    # return html code
    return display(HTML(f'''
        <style type="text/css">
            {CSS}
        </style>

        <div class="tree-container">
            {edges_html}
            {nodes_html}
        </div>
    '''))


CSS = '''
.tree-container {
    position: relative;
    height: 320px;
}

.tree-container .tree-node {
    position: absolute;
    height: 40px;
    
    border: 1px solid rgba(0, 0, 0, 0.5);
    border-radius: 5px;
    background-color: white;
    
    display: flex;
    justify-content: center;
    align-items: center;
}

.tree-container .tree-node.inner {
    width: 80px;
}

.tree-container .tree-node.leaf {
    width: 40px;
}

.tree-container .tree-node.leaf.zero {
    background-color: rgb(255, 200, 200);
}

.tree-container .tree-node.leaf.one {
    background-color: rgb(200, 255, 200);
}

.tree-container .tree-edge {
    position: absolute;
}
'''
