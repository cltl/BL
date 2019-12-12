import networkx as nx


def get_leaf_nodes(g,
                   verbose=0):
    leaf_nodes = set()
    for node in g.nodes():
        descendants = nx.descendants(g, node)
        if not descendants:
            leaf_nodes.add(node)

    if verbose:
        print()
        print(f'found {len(leaf_nodes)} leaf node(s)')

    return leaf_nodes





if __name__ == '__main__':
    edges = [
        (5, 4),
        (4, 3),
        (3, 2),
        (2, 1),
        (3, 1),
        (5, 3),
        (3, 6),
        (6, 7),
        (1, 0)
    ]
    g = nx.DiGraph()
    g.add_edges_from(edges)

    leaf_nodes = get_leaf_nodes(g, verbose=1)
    print(leaf_nodes)
