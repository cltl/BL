import pickle
import sys
import networkx as nx
import pandas as pd
sys.path.append('../')

def plot_graph(a_graph, output_path):
    """

    :param a_graph:
    :return:
    """
    p = nx.drawing.nx_pydot.to_pydot(a_graph)
    p.write_png(output_path)

def table(ev_type_coll_obj, output_path):
    """

    :param ev_type_coll_obj:
    :return:
    """
    list_of_lists = []
    headers = ['Child of root node', '# of descendants', 'Cumulative Incident Frequency']

    children = ev_type_coll_obj.g.successors('Q1656682')

    for child in children:
        ev_type_obj = ev_type_coll_obj.event_type_id_to_event_type_obj[f'http://www.wikidata.org/entity/{child}']
        subsumers = {subsumer
                     for subsumer in ev_type_obj.subsumers
                     if subsumer not in ev_type_coll_obj.leaf_nodes}

        inc_freq = 0
        for subsumer in subsumers:
            subsumer_obj = ev_type_coll_obj.event_type_id_to_event_type_obj[f'http://www.wikidata.org/entity/{subsumer}']
            inc_freq += len(subsumer_obj.incidents)

        one_row = [ev_type_obj.label_to_show, len(subsumers), inc_freq]
        list_of_lists.append(one_row)

    df = pd.DataFrame(list_of_lists, columns=headers)

    if output_path:
        df.to_excel(output_path, index=False)

    return df

# load EventTypeCollection
ev_type_coll = pickle.load(open('../wd_cache/ev_type_coll.p', 'rb'))

print()
print('full graph')
print(ev_type_coll)

# obtain non leaf nodes
non_leaf_nodes = set(ev_type_coll.g.nodes()) - ev_type_coll.leaf_nodes

# subgraph
sub_g = ev_type_coll.g.subgraph(non_leaf_nodes).copy()

print()
print('graph without leaf nodes')
print(nx.info(sub_g))

plot_graph(sub_g, '../output/subgraph.png')

table(ev_type_coll, output_path='../output/children_of_event.xlsx')
