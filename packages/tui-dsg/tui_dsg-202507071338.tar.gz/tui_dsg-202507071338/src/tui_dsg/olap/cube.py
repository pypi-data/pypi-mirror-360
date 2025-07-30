from typing import Any, Dict, Optional

from IPython.display import display, HTML
from pandas import Series


def _draw_cube(s: Series, color: Optional[Series] = None) -> str:
    # generate color series
    if color is None:
        color = Series(dtype=int)

    # extract key names
    x_name, y_name, z_name = s.keys().names

    # reverse keys for drawing
    values: Dict[Any, Dict[Any, Dict[Any, Any]]] = {}
    xs, ys, zs = {}, {}, {}

    for (x, y, z), v in s.items():
        xs[x] = None
        ys[y] = None
        zs[z] = None

        if z not in values:
            values[z] = {}
        vz = values[z]

        if y not in vz:
            vz[y] = {}
        vy = vz[y]

        if x in vy:
            raise AssertionError
        vy[x] = v

    # select offsets
    offset = {
        1: [0],
        2: [1, -1],
        3: [2, 0, -2],
        4: [3, 1, -1, -3]
    }

    x_offsets = offset[len(xs)]
    y_offsets = offset[len(ys)]
    z_offsets = offset[len(zs)]

    # calculate cube positions
    cubes = []

    for zo, zv in zip(z_offsets, reversed(list(zs.keys()))):
        for yo, yv in zip(y_offsets, ys.keys()):
            for xo, xv in zip(x_offsets, xs.keys()):
                left = -22 * xo + 15 * zo
                top = -22 * yo - 10 * zo

                if xv not in s or yv not in s[xv] or zv not in s[xv][yv]:
                    value = '0.00'
                else:
                    value = f'{s[xv][yv][zv]:.2}'

                if xv in color and yv in color[xv] and zv in color[xv, yv]:
                    col = 'filter: invert(50%) sepia(96%) saturate(1854%) hue-rotate(158deg) brightness(90%) contrast(102%);'
                else:
                    col = ''

                cubes.append((left, top, value, col))

    cubes_html = '\n'.join(map(
        lambda c: f'<img src="{FACE}" style="left: calc(50% - 25px + {c[0]}px); top: calc(50% - 25px + {c[1]}px); {c[3]}">'
                  f'<img src="{MESH}" style="left: calc(50% - 25px + {c[0]}px); top: calc(50% - 25px + {c[1]}px);">'
                  f'<div class="value" style="left: calc(50% - 25px + {c[0]}px); top: calc(50% - 25px + 8px + {c[1]}px);">{c[2]}</div>',
        cubes
    ))

    # add axis
    x_pos = -70 - (len(zs) - 1) * 15 - 7.5, len(ys) / 2 * 40 + (len(zs) - 1) * 10 - 5
    y_pos = -len(xs) * 22 - (len(zs) - 1) * 15 - 70 - 10, (len(zs) - 1) / 2 * 7.5
    z_pos = -70 + len(xs) / 2 * 30 + (len(zs) - 1) / 2 * 5 + 25, len(ys) * 22 - (len(zs) - 1) / 2 * 11 - 5

    axis_html = f'''
        <div class="axis x" style="left: calc(50% + {x_pos[0]}px); top: calc(50% + {x_pos[1]}px + 15px)">
            {x_name}
        </div>
        <div class="axis y" style="left: calc(50% + {y_pos[0]}px - 15px); top: calc(50% + {y_pos[1]}px)">
            {y_name}
        </div>
        <div class="axis z" style="left: calc(50% + {z_pos[0]}px + 15px); top: calc(50% + {z_pos[1]}px + 8px)">
            {z_name}
        </div>
    '''

    # add labels
    labels = []

    for xo, xl in zip(x_offsets, reversed(xs.keys())):
        x, y = x_pos
        x += xo * 22
        labels.append(('x', x, y, xl))

    for yo, yl in zip(y_offsets, reversed(ys.keys())):
        x, y = y_pos
        y += yo * 22
        labels.append(('y', x, y, yl))

    for zo, zl in zip(z_offsets, reversed(zs.keys())):
        x, y = z_pos
        x += zo * 15
        y += -zo * 10
        labels.append(('z', x, y, zl))

    labels_html = '\n'.join(map(
        lambda c: f'<div class="axis axis-label {c[0]}" style="left: calc(50% + {c[1]}px); top: calc(50% + {c[2]}px);">'
                  f'{c[3]}'
                  f'</div>',
        labels
    ))

    # create html
    return f'''
        <div class="olap-cube">
            <!-- <div class="marker"></div> -->
            {cubes_html}
            {axis_html}
            {labels_html}
        </div>
    '''


def draw_olap_cube(*s: Series):
    cubes = '\n'.join(map(lambda e: _draw_cube(*e) if isinstance(e, tuple) else _draw_cube(e), s))

    return display(HTML(f'''
        <style type="text/css">
            {CSS}
        </style>

        <div class="olap-container">
            {cubes}
        </div>
    '''))


CSS = '''
.olap-container {
    height: 320px;
    position: relative;
    display: flex;
    flex-direction: row;
}

.olap-cube {
    height: 100%;
    position: relative;
    flex-grow: 1;
}

.olap-cube .marker {
    width: 10px;
    height: 10px;
    border-radius: 5px;

    position: absolute;
    left: calc(50% - 5px);
    top: calc(50% - 5px);
    z-index: 99;

    background-color: red;
}

.olap-cube img {
    margin-top: 0;
    position: absolute;
    width: 50px;
}

.olap-cube .value {
    position: absolute;
    width: 34px;
    height: 34px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 75%;
}

.olap-cube .axis {
    position: absolute;
    font-size: 90%;
    width: 140px;
    height: 30px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.olap-cube .axis.axis-label {
    font-size: 70%;
}

.olap-cube .y {
    transform: rotate(-90deg);
}

.olap-cube .z {
    transform: rotate3d(0.5, 0.5, -1, 45deg)
}
'''

MESH = 'data:image/png;base64,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'
FACE = 'data:image/png;base64,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'
