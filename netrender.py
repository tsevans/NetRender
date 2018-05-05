import argparse
import igraph as ig

# Dictionary used to map indices to vertices in a network
vertex_map = {}


def process_input(input_path):
    """
    Convert input network to IGraph representation.
    :param input_path: Location of network input file.
    :return: IGraph representation of input network.
    """
    pass


def render_network():
    """
    Render network in three-dimensional space.
    :return:
    """
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
    parser.add_argument('-c', '--color', help='change color scale of network', type=str)
    args = parser.parse_args()
    print(args.color)


if __name__ == '__main__':
    main()
