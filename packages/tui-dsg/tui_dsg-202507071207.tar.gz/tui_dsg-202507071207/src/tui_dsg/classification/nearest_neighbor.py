from uuid import uuid4

import pandas as pd
from IPython.display import display, HTML
from sklearn.cluster import KMeans


def draw_nn(df: pd.DataFrame, k: int = 1, cluster: int = None):
    random_id = str(uuid4())

    # normalize coordinates
    points_df = df.copy()

    df['x'] = (df['x'] - df['x'].min()) / (df['x'].max() - df['x'].min()) * 90 + 5
    df['y'] = (df['y'] - df['y'].min()) / (df['y'].max() - df['y'].min()) * 90 + 5
    df['c'] = df['c'].replace({
        'A': '#636EFA',
        'B': '#EF553B',
        'C': '#00CC96'
    })

    # apply k-means clustering
    if cluster is None:
        bg_df = pd.DataFrame()

    else:
        centroids = KMeans(n_clusters=cluster).fit(df[['x', 'y']]).cluster_centers_
        colors = []

        for x, y in zip(centroids[:, 0], centroids[:, 1]):
            squared_distances = (df['x'] - x) ** 2 + (df['y'] - y) ** 2
            min_distance_index = squared_distances.argmin()
            colors.append(df['c'][min_distance_index])

        bg_df = points_df
        df = pd.DataFrame({
            'x': centroids[:, 0],
            'y': centroids[:, 1],
            'c': colors
        })

    # points_html
    points = []

    for t, d in ('bg', bg_df), ('fg', df):
        for _, row in d.iterrows():
            left = f'calc({row["x"]}% - 5px)'
            top = f'calc({row["y"]}% - 5px)'
            color = row['c']

            points.append(
                f'<div class="point {t}" style="left: {left}; bottom: {top}; background-color: {color}"></div>'
            )

    points_html = '\n'.join(points)

    # return HTML
    return display(HTML(f'''
        <style type="text/css">
            {CSS}
        </style>
        
        <div id="animation-container-{random_id}" class="animation-container">
            {points_html}
            
            <div class="draggable">
        </div>
        
        <script type="text/javascript">
            {JS}
            
            init("{random_id}", {k});
        </script>
    '''))


CSS = '''
.animation-container {
    position: relative;
    height: 400px;
    background-color: #e5ecf6;
}

.animation-container .point {
    width: 8px;
    height: 8px;
    border-radius: 4px;

    position: absolute;
}

.animation-container .point.bg {
    width: 4px;
    height: 4px;
    border-radius: 2px;

    opacity: 0.5;
}

.animation-container .active {
    box-shadow: 0 0 5px 2px rgba(0, 0, 0, 1);
    z-index: 9;
}

.animation-container .draggable {
    width: 20px;
    height: 20px;
    border-radius: 10px;

    position: absolute;
    left: calc(50% - 10px);
    top: calc(50% - 10px);

    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgb(60, 60, 60);
}
'''

JS = '''
// useful functions
function getRelativeMousePosition(container, event) {
    const x = (event.clientX - container.getBoundingClientRect().x) / container.getBoundingClientRect().width;
    const y = (event.clientY - container.getBoundingClientRect().y) / container.getBoundingClientRect().height;

    return {
        x: Math.max(0.05, Math.min(0.95, x)),
        y: Math.max(0.05, Math.min(0.95, y)),
    }
}

function squaredEuclidianDistance(p1, p2) {
    const p1x = p1.offsetLeft + p1.offsetWidth / 2;
    const p1y = p1.offsetTop + p1.offsetHeight / 2;
    const p2x = p2.offsetLeft + p2.offsetWidth / 2;
    const p2y = p2.offsetTop + p2.offsetHeight / 2;

    return Math.pow(p2x - p1x, 2) + Math.pow(p2y - p1y, 2);
}

// nearest neighbour implementations
/*
function nearestNeighbour(draggable, points) {
    // get the closest point's color
    let minDistance = Number.POSITIVE_INFINITY;
    let minPoint = null;

    for (let point of points) {
        const distance = squaredEuclidianDistance(draggable, point);
        if (distance < minDistance) {
            minDistance = distance;
            minPoint = point;
        }
    }

    // assign active class to points
    for (let point of points)
        point.classList.remove('active');

    minPoint.classList.add('active');

    // assign color to draggable
    draggable.style.backgroundColor = minPoint.style.backgroundColor;
}
*/

function kNearestNeighbour(draggable, points, k) {
    // sort points by distance to draggable
    const distances = Array.from(points).map(p => {
        return {
            'p': p,
            'd': squaredEuclidianDistance(p, draggable)
        }
    }).sort((a, b) => a.d - b.d);

    // highlight k nearest neighbours
    distances.slice(0, k).forEach(v => v.p.classList.add('active'));
    distances.slice(k).forEach(v => v.p.classList.remove('active'));

    // majority vote
    const classes = distances.slice(0, k).reduce((a, v) => {
        a[v.p.style.backgroundColor] = a[v.p.style.backgroundColor] ? a[v.p.style.backgroundColor] + 1 : 1;
        return a;
    }, {});

    draggable.style.backgroundColor = Object.keys(classes)
        .reduce((a, k) => (a === null || classes[k] > classes[a] ? k : a));
}

// init function
function init(suffix, k) {
    const container = document.getElementById(`animation-container-${suffix}`);

    const draggable = container.querySelector('.draggable');
    const points = container.querySelectorAll('.fg');

    // mouse event handlers
    let dragActive = false;
    let lastAction = 0;
    let timer = 0;

    function mousemove(e) {
        if (!dragActive)
            return;

        // debounce
        const timestamp = (new Date()).getTime();
        const delay = lastAction + 30 - timestamp;

        window.clearTimeout(timer);
        timer = window.setTimeout(() => {
            // update position
            const pos = getRelativeMousePosition(container, e);
            draggable.style.left = `calc(${pos.x * 100}% - ${draggable.offsetWidth / 2}px)`;
            draggable.style.top = `calc(${pos.y * 100}% - ${draggable.offsetHeight / 2}px)`;

            // update color
            kNearestNeighbour(draggable, points, k);
        }, Math.max(delay, 0));
    }

    function mousedown(e) {
        dragActive = true;
        mousemove(e);
    }

    function mouseup(e) {
        mousemove(e);
        dragActive = false;
    }

    container.addEventListener('mousedown', mousedown);
    container.addEventListener('mouseup', mouseup);
    container.addEventListener('mousemove', mousemove);

    // set draggable's initial color
    kNearestNeighbour(draggable, points, k);
}
'''
