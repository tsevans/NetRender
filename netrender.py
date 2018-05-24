import sys
import argparse
from binascii import crc32
import igraph as ig
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

    # Print graph information
    print(str(len(vertices)) + ' vertices')
    print(str(len(edges)) + ' edges')

    # Build IGraph representation of network
    graph = ig.Graph(edges, directed=False)
    graph.es['weight'] = [weights[e] for e in range(len(graph.es))]

    return graph, vertices


def hash_colors(vertex):
    """
    Generate a unique color for a vertex based on it's hashed name.
    :param vertex: The vertex to generate a color for.
    :return: Tuple of (R, G, B) color values for the vertex.
    """

    def calculate_colors(v):
        """
        Calculate the color for name of the given vertex v.
        :param v: Name of vertex to be hashed.
        :return: Tuple of (hue, saturation, lightness) values.
        """

        # Define constant color values
        lightness = [0.35, 0.5, 0.65]
        saturation = [0.35, 0.5, 0.65]

        # Calculate the CRC-32 checksum of colors encoded as a UTF-8 string
        hash = crc32(str(v).encode('utf-8')) & 0xffffffff

        # Calculate the HSL (hue, saturation, lightness) values for the vertices
        hue = ((hash % 359) / 1000) * 360
        hash //= 360
        sat = saturation[hash % len(saturation)]
        hash //= len(saturation)
        lig = lightness[hash % len(lightness)]

        return (hue, sat, lig)

    def hsl_to_rgb(hsl):
        """
        Convert HSL color value into RGB.
        :param hsl: HSL values for given vertex.
        :return: Tuple of (R, G, B) colors for vertex.
        """
        try:
            h, s, l = hsl
        except TypeError:
            raise ValueError(hsl)
        try:
            h /= 360
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
        except TypeError:
            raise ValueError(hsl)

        rgb = []
        for c in (h + 1 / 3, h, h - 1 / 3):
            if c < 0:
                c += 1
            elif c > 1:
                c -= 1

            if c < 1 / 6:
                c = p + (q - p) * 6 * c
            elif c < 0.5:
                c = q
            elif c < 2 / 3:
                c = p + (q - p) * 6 * (2 / 3 - c)
            else:
                c = p
            rgb.append(round(c * 255))

        return tuple(rgb)

    raw_hsl = calculate_colors(vertex)
    return hsl_to_rgb(raw_hsl)


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
        c = hash_colors(v)
        color = 'rgb('
        if color_scale is None:
            color += '%s,%s,%s)' % tuple(c)
        elif color_scale == 'red':
            color += '255,%s,%s)' % (c[1], c[2])
        elif color_scale == 'green':
            color += '%s,255,%s)' % (c[0], c[2])
        elif color_scale == 'blue':
            color += '%s,%s,255)' % (c[0], c[1])
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


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('filename',
                        nargs='+')
    parser.add_argument('-v',
                        help='increase output verbosity',
                        action='store_true')
    parser.add_argument('-c',
                        help='change color scale of network',
                        type=str,
                        choices=['red', 'green', 'blue'])
    args = parser.parse_args()

    graph, vertices = process_input(args.filename[0])
    render_network(graph, args.c, vertices)
    pass


if __name__ == '__main__':
    main()
