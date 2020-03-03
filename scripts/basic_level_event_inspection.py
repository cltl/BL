import pickle
import sys
import shutil
import os
import json
import operator

import networkx as nx
import pandas as pd
import graphviz
sys.path.append('../')

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

def keys_with_highest_n_values(a_dict, n, min_value=0):
    """

    :param dict a_dict: a dictionary mappings keys to integers or floats
    :param n: the keys you want to return with the n highest values

    :rtype: set
    :return: set of keys with n highest values
    """
    selected_keys = set()
    for index, (key, value) in enumerate(sorted(a_dict.items(),
                                         key=operator.itemgetter(1),
                                         reverse=True), 1):

        if value >= min_value:
            selected_keys.add(key)
        if index == n:
            break

    return selected_keys

result = keys_with_highest_n_values({'a' : 2, 'b': 1, 'c': 3}, 2)
assert result == {'a', 'c'}


def plot_graph(a_graph, output_path):
    """

    :param a_graph:
    :return:
    """
    p = nx.drawing.nx_pydot.to_pydot(a_graph)
    p.write_png(output_path)


def table(ev_type_coll_obj, dot_folder, excel_path):
    """

    :param ev_type_coll_obj:
    :return:
    """
    list_of_lists = []
    headers = ['Child of root node', 'Q ID', '# of descendants', 'Cumulative Incident Frequency']

    children = ev_type_coll_obj.g.successors(EVENT_NODE)

    for child in children:
        ev_type_obj = ev_type_coll_obj.event_type_id_to_event_type_obj[f'http://www.wikidata.org/entity/{child}']
        subsumers = {subsumer
                     for subsumer in ev_type_obj.subsumers
                     if subsumer not in ev_type_coll_obj.leaf_nodes}

        inc_freq = 0
        for subsumer in subsumers:
            subsumer_obj = ev_type_coll_obj.event_type_id_to_event_type_obj[f'http://www.wikidata.org/entity/{subsumer}']
            inc_freq += len(subsumer_obj.incidents)

        #dot_path = os.path.join(dot_folder, f'{child}.png')
        #subgraph = nx.subgraph(ev_type_coll_obj.g, subsumers)
        #plot_graph(subgraph, dot_path)

        one_row = [ev_type_obj.label_to_show, child, len(subsumers), inc_freq]
        list_of_lists.append(one_row)

    df = pd.DataFrame(list_of_lists, columns=headers)
    df.sort_values('Cumulative Incident Frequency', inplace=True, ascending=False)

    if excel_path:
        df.to_excel(excel_path, index=False)

    return df


def selection_of_leaf_nodes(a_graph, event_coll_obj, leaf_nodes, verbose=0):
    """

    :param a_graph:
    :param event_coll_obj:
    :param leaf_node:
    :return:
    """
    keep = set()
    remove = set()

    # get siblings
    all_parents = set()
    for leaf_node in leaf_nodes:
        parents = a_graph.predecessors(leaf_node)
        all_parents.update(parents)

    if verbose >= 1:
        print()
        print(f'found {len(all_parents)} parents of leaf nodes')

    for parent in all_parents:

        children = list(a_graph.successors(parent))

        leaf_node_children = {child
                              for child in children
                              if child in leaf_nodes}

        child_to_inc_freq = {}
        for leaf_node_child in leaf_node_children:

            ev_obj = event_coll_obj.event_type_id_to_event_type_obj[f'http://www.wikidata.org/entity/{leaf_node_child}']
            inc_freq = len(ev_obj.incidents)
            child_to_inc_freq[leaf_node_child] = inc_freq



        selected_leaf_children = keys_with_highest_n_values(child_to_inc_freq,
                                                            n=2,
                                                            min_value=MIN_INC_FREQ_FOR_LEAF_NODES)

        keep.update(selected_leaf_children)

    remove = leaf_nodes - keep

    if verbose >= 1:
        print()
        print(f'from the {len(leaf_nodes)} leaf nodes')
        print(f'{len(keep)} were included')
        print(f'{len(remove)} were removed')

    assert (keep | remove) == leaf_nodes

    return keep, remove

def determine_sample(subgraph,
                     dot_folder,
                     event_coll_obj,
                     selected_children,
                     remove_subgraphs,
                     verbose
                     ):
    """

    :param networkx.classes.digraph.DiGraph subgraph: a networkx directed graph
    :param EventTypeCollection event_coll_obj: instance of EventTypeCollection (as found in ../wd_classes.py)
    :param set selected_children: the children of the event node that are included in the annotation
    :param int verbose: increase for more information

    :rtype: networkx.classes.digraph.DiGraph
    :return: trimmed directed graph containing only the edges selected to annotate
    """
    # subgraphs to remove
    nodes_of_subgraphs_to_remove = set()
    for subgraph_to_remove in remove_subgraphs:
        subsumers = nx.descendants(subgraph, subgraph_to_remove)
        nodes_of_subgraphs_to_remove.add(subgraph_to_remove)
        nodes_of_subgraphs_to_remove.update(subsumers)

        if verbose >= 1:
            print()
            print(f'removed subgraph {subgraph_to_remove} with {len(subsumers)} subsumers')

    # determine all subsumers all selected children
    relevant_nodes = set([EVENT_NODE])
    for selected_child in selected_children:
        child_subsumers = nx.descendants(subgraph, selected_child)
        relevant_nodes.add(selected_child)
        relevant_nodes.update(child_subsumers)

        if verbose >= 3:
            print()
            print(f'child of event node {selected_child} has {len(child_subsumers)} subsumers')

    relevant_nodes = relevant_nodes - nodes_of_subgraphs_to_remove

    trimmed_graph = nx.subgraph(subgraph, relevant_nodes)
    plot_graph(trimmed_graph, os.path.join(dot_folder, 'trimmed_graph.png'))

    if verbose >= 1:
        print()
        print(f'obtained {len(relevant_nodes)} selected nodes from {selected_children}')
        print(f'trimmed graph has the following information:')
        print(nx.info(trimmed_graph))

    leaf_nodes = get_leaf_nodes(trimmed_graph)

    if verbose >= 2:
        print(f'found {len(leaf_nodes)} leaf nodes in trimmed graph')

    keep, remove = selection_of_leaf_nodes(trimmed_graph, event_coll_obj, leaf_nodes, verbose=verbose)

    sample_nodes = relevant_nodes - remove
    sample_graph = nx.subgraph(trimmed_graph, sample_nodes)

    if verbose >= 1:
        print()
        print('sample graph')
        print(nx.info(sample_graph))
        plot_graph(sample_graph, os.path.join(dot_folder, 'sample_graph.png'))

    return sample_graph


def convert_to_images(graph, ev_coll_obj, images_folder, annotations_folder, verbose=0):
    """

    :param networkx.classes.digraph.DiGraph graph: the graph containing only edges to annotate
    :param str images_folder: the folder where the images, each image of one edge, are stored
    :param str annotations_folder: the folder where the JSON with the annotations are stored
    """
    for folder in [images_folder, annotations_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)

    annotations = dict()
    id_to_edge = dict()

    for id_, (parent, child) in enumerate(graph.edges(), 1):

        # create image
        child_label = ev_coll_obj.event_type_id_to_event_type_obj[f'http://www.wikidata.org/entity/{child}'].label_to_show
        parent_label = ev_coll_obj.event_type_id_to_event_type_obj[f'http://www.wikidata.org/entity/{parent}'].label_to_show

        dot_string = '\n'.join([
            "digraph G {",
            f'0[label="{parent_label}"];',
            f'1[label="{child_label}"];'
            '',
            '0 -> 1[dir=back, label="subclass of"];',
            '}'])
        source_obj = graphviz.Source(source=dot_string,
                                     format='svg')
        source_obj.render(directory=images_folder,
                          filename=f'{id_}',
                          format='svg')


        annotations[id_] = False
        id_to_edge[id_] = [parent, child]

    path_annotations = os.path.join(annotations_folder, 'annotations.json')
    path_id_to_edge = os.path.join(annotations_folder, 'id_to_edge.json')

    for (json_path, a_dict) in [(path_annotations, annotations),
                                (path_id_to_edge, id_to_edge)]:
        with open(json_path, 'w') as outfile:
            json.dump(a_dict, outfile)

    if verbose >= 1:
        print(f'written annotations to {path_annotations}')
        print(f'written id_to_edge to {path_id_to_edge}')

def export(export_folder, settings, images_folder, annotations_folder, path_the_end_svg):
    """

    :param str export_folder: where the data release will be stored
    (overwritten if exists)
    :param dict settings: the settings used to generate the data
    :param str images_folder: where the svg files are stored
    :param str annotations_folder: where the JSON with annotations are stored
    :param str path_the_end_svg: path to the_end.svg image
    """
    # create folder (remove if exists)
    if os.path.exists(export_folder):
        shutil.rmtree(export_folder)
    os.mkdir(export_folder)

    # save settings
    settings_path = os.path.join(export_folder, 'settings.json')
    with open(settings_path, 'w') as outfile:
        json.dump(settings, outfile)

    # copy images folder
    export_images_folder = os.path.join(export_folder, 'images')
    shutil.copytree(images_folder,
                    export_images_folder)

    # cp the_end.svg
    shutil.copy(path_the_end_svg,
                os.path.join(export_images_folder, 'the_end.svg')
                )

    # annotations
    export_anno_folder = os.path.join(export_folder, 'annotations')
    shutil.copytree(annotations_folder,
                    export_anno_folder)


# paths
ev_type_coll_path = '../wd_cache/ev_type_coll.p'
out_dir = '../basic_level_inspection'
dot_folder = os.path.join(out_dir, 'dot')
images_folder = os.path.join(out_dir, 'images')
annotations_folder = os.path.join(out_dir, 'annotations')

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.mkdir(out_dir)
os.mkdir(dot_folder)

EVENT_NODE = 'Q1656682'
MIN_INC_FREQ_FOR_LEAF_NODES = 25
TOP_TEN =  ["Q13406554",
            "Q15275719","Q1856757","Q189760","Q464980",
            "Q645883","Q2627975","Q2761147","Q35140","Q625994"]
SELECTED_CHILDREN = ["Q200538"]
REMOVE_SUBGRAPH = ['Q1864008']
export_folder = '../data_releases/test'
path_the_end_svg = 'the_end.svg'

SETTINGS = {
    'root' : EVENT_NODE,
    'min_inc_freq_for_leaf_nodes' : MIN_INC_FREQ_FOR_LEAF_NODES,
    'selected_children' : SELECTED_CHILDREN,
    'removed_subgraphs' : REMOVE_SUBGRAPH
}

# load EventTypeCollection
ev_type_coll = pickle.load(open(ev_type_coll_path, 'rb'))

print()
print('full graph')
print(ev_type_coll)

# obtain non leaf nodes
non_leaf_nodes = set(ev_type_coll.g.nodes()) - ev_type_coll.leaf_nodes

# subgraph
sub_g = ev_type_coll.g.subgraph(non_leaf_nodes).copy()


print(type(sub_g))

print()
print('graph without leaf nodes')
print(nx.info(sub_g))

plot_graph(sub_g, f'{dot_folder}/graph_no_leaf_nodes.png')

table(ev_type_coll,
      dot_folder,
      excel_path=f'{out_dir}/children_of_event.xlsx')


sample_graph = determine_sample(subgraph=sub_g,
                                dot_folder=dot_folder,
                                event_coll_obj=ev_type_coll,
                                selected_children=SELECTED_CHILDREN,
                                remove_subgraphs=REMOVE_SUBGRAPH,
                                verbose=2)

convert_to_images(graph=sample_graph,
                  ev_coll_obj=ev_type_coll,
                  images_folder=images_folder,
                  annotations_folder=annotations_folder,
                  verbose=2)


export(export_folder=export_folder,
       settings=SETTINGS,
       images_folder=images_folder,
       annotations_folder=annotations_folder,
       path_the_end_svg=path_the_end_svg)