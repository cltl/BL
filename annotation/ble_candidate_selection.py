import sys
sys.path.append('../')
import utils

import pickle
import networkx as nx
import json


# result of calling MWEP repository utils.load_ontology_as_directed_graph
graph_path = 'input/g.p'

# path to all paths (any BLCollection suffices since all paths are stored from leaf nodes to event node
bl_coll_obj_path = 'input/resource=Wikidata+rootnode=wd:Q1656682+rootzero=True+weightproperty=occurrence_frequency+threshold=0.p'
bl_coll_obj = pickle.load(open(bl_coll_obj_path, 'rb'))
g = nx.read_gpickle(graph_path)

print(nx.info(g))

num_leaf_nodes = len(bl_coll_obj.leaf_nodes)

print(f'number of leaf nodes', num_leaf_nodes)

all_paths, edge2freq, edge2children = utils.get_paths(bl_coll_obj, g, verbose=2)

verbose = 2
forbidden_in_path = {'wd:Q327197'}

df = utils.target_df(g=g,
                     min_freq=5,
                     min_descendants=0,
                     min_num_children=1,
                     forbidden_in_path=set())
print(len(df))

df = utils.target_df(g=g,
                     min_freq=5,
                     min_descendants=0,
                     min_num_children=3,
                     forbidden_in_path=forbidden_in_path)
print(len(df))


node_id2tree_info = {}

for index, row in df.iterrows():

    nodes = set()
    edges = list()

    central_node_id = row['ID']

    # path to top
    paths_to_top = row['paths_to_event_node']
    for path in paths_to_top:
        for source, target in zip(path,
                                  path[1:]):
            if (source, target) not in edges:
                edges.append((source, target))
            nodes.update([source, target])

    # children
    for child in row['chosen_children']:
        nodes.add(child)
        if (child, central_node_id) not in edges:
            edges.append((central_node_id, child))

    node_id2tree_info[central_node_id] = {
        'nodes': list(nodes),
        'edges': [list(item) for item in edges],
        'parents' : row['parents'],
    }


with open('input/to_annotate.json', 'w') as outfile:
    json.dump(node_id2tree_info, outfile)