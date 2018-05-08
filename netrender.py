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


def run_test(case):
    """
    Run one of the pre-made test cases when the -t option is passed from the command line.
    :param case: Choice for test to run, should be pre-validated through command line.
    """
    if case == 'mouse':
        print('testing ' + case)
    elif case == 'cat':
        print('testing ' + case)
    elif case == 'macaque':
        print('testing ' + case)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-v', help='increase output verbosity', action='store_true')
    parser.add_argument('-c', help='change color scale of network', type=str, choices=['red', 'green', 'blue'])
    parser.add_argument('-t', help='test program on an existing connectome', choices=['mouse', 'cat', 'macaque'])
    args = parser.parse_args()
    if args.t is not None:
        run_test(args.t)
    else:
        print(args.c)


if __name__ == '__main__':
    main()
