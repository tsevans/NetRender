import sys
import argparse
import igraph as ig
from colorhash import ColorHash
import plotly.offline as py
from plotly.graph_objs import *


def process_input(input_path):
    """
    Convert input network to IGraph representation.
    :param input_path: Location of network input file.
    :return: IGraph representation of input network.
    """

    # Parse lines from input file into list
    with open(input_path, 'r') as input_file:
        lines = input_file.readlines()

    # Declare component lists and helper variables
    vertex_map = {}  # Mapping of named vertices to indices, handles duplicate connections
    idx = 0
    edges = []  # List of (src, dst) tuples
    weights = []  # Weight of each edge

    for line in lines:
        # Parse each line of csv or text file
        if input_path.endswith('.csv'):
            parts = line.split(',')
        else:
            parts = line.split()

        # Add source vertex to list of vertices
        src = parts[0]
        if src not in vertex_map:
            vertex_map[src] = idx
            idx += 1

        # Add destination vertex to list of vertices
        dst = parts[1]
        if dst not in vertex_map:
            vertex_map[dst] = idx
            idx += 1

        # Add integer representation of edges to list of connections
        edges.append((vertex_map[src], vertex_map[dst]))
        weights.append(parts[2])

    # Get definite list of vertices
    vertices = vertex_map.keys()

    print(idx)

    # Print graph information
    print(str(len(vertices)) + ' vertices')
    print(str(len(edges)) + ' edges')

    # Build IGraph representation of network
    graph = ig.Graph(edges, directed=False)
    graph.es['weight'] = [weights[e] for e in range(len(graph.es))]

    return graph, vertices


def render_network(graph, color_scale, vertices):
    """
    Render network in three-dimensional space.
    :param graph: IGraph representation of input network.
    :param color_scale:
    :param vertices:
    """

    layout = graph.layout('kk', dim=3)

    # Generate colors for each vertex based on hash value of their names
    colors = []
    for v in vertices:
        c = ColorHash(v)
        color = 'rgb('
        if color_scale is not None:
            pass
        else:
            color += '%s,%s,%s)' % tuple(c.rgb)
        colors.append(color)

    # Build plot.ly trace for vertices
    v_trace = Scatter3d(
        x=[layout[k][0] for k in range(len(vertices))],  # x-coordinates of vertices
        y=[layout[k][1] for k in range(len(vertices))],  # y-coordinates of vertices
        z=[layout[k][2] for k in range(len(vertices))],  # z-coordinates of vertices
        name='nodes',
        mode='markers',
        marker=Marker(
            symbol='dot',
            size=10,
            color=colors,
            line=Line(
                color='rgb(50,50,50)',
                width=0.5)),
        text=vertices,
        hoverinfo='text')

    # Build plot.ly trace for edges
    x_edge, y_edge, z_edge = ([] for i in range(3))
    for e in graph.get_edgelist():
        x_edge += [layout[e[0]][0], layout[e[1]][0], None]  # x-coordinates of edge endings
        y_edge += [layout[e[0]][1], layout[e[1]][1], None]  # y-coordinates of edge endings
        z_edge += [layout[e[0]][2], layout[e[1]][2], None]  # z-coordinates of edge endings
    e_trace = Scatter3d(
        x=x_edge,
        y=y_edge,
        z=z_edge,
        mode='lines',
        line=Line(
            color='rgb(0,0,0)',
            width=1),
        hoverinfo='none')

    # Build plot.ly layout
    axis = dict(showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False, title='')
    layt = Layout(
        title="3D Visualization of Brain Network",
        showlegend=False,
        scene=Scene(
            xaxis=XAxis(axis),
            yaxis=YAxis(axis),
            zaxis=ZAxis(axis)),
        margin=Margin(t=100),
        hovermode='closest')

    data = Data([e_trace, v_trace])
    figure = Figure(data=data, layout=layt)
    py.plot(figure)


def run_test(case):
    """
    Run one of the pre-made test cases when the -t option is passed from the command line.
    :param case: Choice for test to run, should be pre-validated through command line.
    """
    if case == 'mouse':
        graph, vertices = process_input('examples/mouse_connectome.txt')
        render_network(graph, None, vertices)
    elif case == 'cat':
        graph, vertices = process_input('examples/cat_connectome.txt')
        render_network(graph, None, vertices)
    elif case == 'macaque':
        graph, vertices = process_input('examples/macaque_connectome.txt')
        render_network(graph, None, vertices)
    else:
        print('Error: Test not found!')
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('filename', nargs='+')
    parser.add_argument('-t', help='test program on an existing connectome', choices=['mouse', 'cat', 'macaque'])
    parser.add_argument('-v', help='increase output verbosity', action='store_true')
    parser.add_argument('-c', help='change color scale of network', type=str, choices=['red', 'green', 'blue'])
    args = parser.parse_args()
    if args.t is not None:
        print(args.t)
        run_test(args.t)

    graph, vertices = process_input(args.filename[0])
    render_network(graph, args.c, vertices)
    pass


if __name__ == '__main__':
    main()
