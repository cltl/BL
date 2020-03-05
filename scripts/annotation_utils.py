import os
import json
from collections import Counter, defaultdict
import pandas as pd
import networkx as nx

ANNOTATION_TASKS = ["participants", "subevents"]

TASK_TO_INDEX = {
    'participants' : 0,
    'subevents' : 1
}

def load_user_annotations(user_annotations_folder, annotation_task, batches, verbose=0):
    """
    Load the user annotations for
    a) one annotation task
    b) n batches

    :rtype: dict
    :return: mapping from (src, tgt) -> value
    """
    user_annotations = dict()
    index = TASK_TO_INDEX[annotation_task]


    for batch in batches:
        folder_path = os.path.join(user_annotations_folder, batch)
        anno_json_path = os.path.join(folder_path, 'annotations', 'annotations.json')
        index_json_path = os.path.join(folder_path, 'annotations', 'id_to_edge.json')
        assert os.path.exists(anno_json_path)

        with open(anno_json_path) as infile:
            anno = json.load(infile)

        with open(index_json_path) as infile:
            id_to_edge = json.load(infile)

        for id_, values in anno.items():

            if id_ == 'the_end':
                continue


            if values == False:
                string_value = 'dk'
            elif type(values) == list:
                string_value = values[index]

            edge = id_to_edge[id_] # edges is (parent, child)

            if string_value in {'dk', 'ns'}:
                value = string_value
            elif string_value in {'1', '2', '3', '4', '5', '6', '7'}:
                value = int(string_value)
            else:
                raise Exception(f'provided annotation {string_value} for id {id_} is not valid. Please inspect.')

            key = tuple(edge)

            if key in user_annotations:
                print()
                print(f'found existing annotation for {key}: skipping')
                continue
            user_annotations[tuple(edge)] = value

    if verbose >= 1:
        print()
        print(f'folder {user_annotations_folder}')
        print(f'annotation task: {annotation_task}')
        print(f'batches: {batches}')
        print(f'# of items annotated: {len(user_annotations)}')
        print(Counter(user_annotations.values()))

    return user_annotations


def combine_annotations(users, batches, main_anno_folder, verbose=0):
    edge_to_user_to_task_to_value = dict()

    for user in users:

        for task in ANNOTATION_TASKS:
            print()
            print(f'working on task {task} for user {user}')
            user_annotations_folder = os.path.join(main_anno_folder, user)
            edge_to_value = load_user_annotations(user_annotations_folder=user_annotations_folder,
                                                  annotation_task=task,
                                                  batches=batches,
                                                  verbose=verbose)

            for edge, value in edge_to_value.items():
                if edge not in edge_to_user_to_task_to_value:
                    info = {user : {task : None}
                            for user in users
                            for task in ANNOTATION_TASKS}
                    edge_to_user_to_task_to_value[edge] = info

                edge_to_user_to_task_to_value[edge][user][task] = value

    return edge_to_user_to_task_to_value


def compute_agreement(edge_to_user_to_task_to_value,
                      annotation_task,
                      output_folder,
                      verbose=0):
    """
    create a table in which the user agreement for a particular task is shown

    """
    category_to_edges = defaultdict(list)

    for edge, user_to_task_to_value in edge_to_user_to_task_to_value.items():

        values = [task_to_value[annotation_task]
                  for user, task_to_value in user_to_task_to_value.items()]

        if values == ['dk' , 'dk']:
            if verbose >= 2:
                print(f'discarded {edge} {annotation_task} because both annotators indicated "dk"')
            continue

        if values == ['ns' , 'ns']:
            if verbose >= 2:
                print(f'discarded {edge} {annotation_task} because both annotators indicated "ns"')
            continue

        category = "other"
        if all([type(value) == int
                for value in values]):
            category = abs(values[0] - values[1]) # we focus on two annotators

        category_to_edges[category].append(edge)

    # create table
    list_of_lists = []
    headers = ['Delta between annotations', 'Number of items']

    for category, edges in category_to_edges.items():
        one_row = [category, len(edges)]
        list_of_lists.append(one_row)

    df = pd.DataFrame(list_of_lists, columns=headers)

    # export table
    excel_path = os.path.join(output_folder, f'agreement_{annotation_task}.xlsx')
    df.to_excel(excel_path, index=False)

    if verbose >= 1:
        print()
        print(f'saved agreement for {annotation_task} to {excel_path}')

    latex_path = os.path.join(output_folder, f'agreement_{annotation_task}.tex')
    df.to_latex(latex_path, index=False)

    if verbose >= 1:
        print()
        print(f'saved agreement for {annotation_task} to {latex_path}')


def load_graph_from_edgelist(path_to_edge_list, verbose=0):
    """
    :param str path_to_edge_list: load graph from edge list
    """
    g = nx.read_edgelist(path_to_edge_list, create_using=nx.DiGraph())

    if verbose:
        print()
        print(f'loaded edge list from: {path_to_edge_list}')
        print(nx.info(g))
    return g


def update_sample_graph_with_annotations(sample_graph,
                                         edge_to_user_to_task_to_value,
                                         verbose=0):
    """

    :param sample_graph: the directed graph selected for annotation
    :param edge_to_user_to_task_to_value: a mapping
    from edge to user to task to value

    :return: the same graph but with the annotations added
    as attributes to the edges
    """
    all_edge_attrs = {}

    for edge, user_to_task_to_value in edge_to_user_to_task_to_value.items():
        edge_attrs = {task : {}
                      for task in ANNOTATION_TASKS}

        for user, task_to_value in user_to_task_to_value.items():
            for task, value in task_to_value.items():
                edge_attrs[task][user] = value

        all_edge_attrs[edge] = edge_attrs

    nx.set_edge_attributes(sample_graph, all_edge_attrs)

    if verbose:
        print()
        print(f'update edge attributes for {len(all_edge_attrs)} edges')

    return sample_graph


def get_average_edge_value(g, edge, annotation_task, users, verbose=0):
    """

    :param g:
    :param edge:
    :param annotation_task:
    :return:
    """
    values = []
    u, v = edge
    attrs = g.get_edge_data(u, v)

    if attrs:
        for user, value in attrs[annotation_task].items():
            if type(value) == int:
                values.append(value)

    if len(values) != len(users):
        values = []

    if values:
        avg = sum(values) / len(values)
    else:
        avg = None

    if verbose >= 4:
        if values:
            print(values)

    return avg


def determine_candidate_basic_levels(g, annotation_task, users, verbose=0):
    """
    Determine nodes with:
    a) annotations in edges from children to candidate basic level
    b) annotations in edges from candidate basic levels to superordinate events

    for debugging purposes:
    a) edge sport:67
    -from Q13406554 (sports competition)
    -to Q16510064 (sporting event)
    -edge in JSON ["Q13406554", "Q16510064"]
    -participants: Piek: 3, Antske: 3
    -subevents: Piek: 3, Antske: 3

    b) edge sport:34
    -from Q16510064 (sporting event)
    -to Q46190676 (tennis event)
    - edge in JSON ["Q16510064", "Q46190676"]
    -participants: Piek: 3, Antske: 2
    -subevents: Piek: 3, Antske: 4

    :rtype: dict
    :return: mapping from event_id ->
    {
    “children” -> avg from edges,
    “parents” -> avg from edges
    }
    """
    ev_to_anno_info = {}

    for node in g.nodes():

        children = g.successors(node)
        parents = g.predecessors(node)

        children_edges = [(node, child)
                           for child in children]
        assert len(children_edges) == len(set(children_edges))

        parent_edges = [(parent, node)
                        for parent in parents]
        assert len(parent_edges) == len(set(parent_edges))

        for parent, child in children_edges + parent_edges:
            assert g.has_edge(parent, child), f'{(parent, child)} not found in graph'

        if any([not children_edges,
                not parent_edges]):
            continue

        children_avgs = []
        for children_edge in children_edges:
            child_edge_avg = get_average_edge_value(g, children_edge, annotation_task, users, verbose=verbose)
            if child_edge_avg is not None:
                children_avgs.append(child_edge_avg)

        parent_avgs = []
        for parent_edge in parent_edges:
            parent_edge_avg = get_average_edge_value(g, parent_edge, annotation_task, users, verbose=verbose)
            if parent_edge_avg is not None:
                parent_avgs.append(parent_edge_avg)

        if any([not children_avgs,
                not parent_avgs]):
            continue

        children_value = sum(children_avgs) / len(children_avgs)
        parent_value = sum(parent_avgs) / len(parent_avgs)
        delta = children_value - parent_value
        result = {
            'children': children_value,
            'parents': parent_value,
            'delta' : delta
        }

        if verbose >= 3:
            print()
            print(node)
            print('children', children_edges)
            print('children averages', children_avgs)
            print('parents', parent_edges)
            print('parent averages', parent_avgs)
            print(result)

        ev_to_anno_info[node] = result

    if verbose:
        print()
        print(f'collected relevant BLE annotation information for {len(ev_to_anno_info)} nodes')

    return ev_to_anno_info


def ble_analysis(candidate_ble_info,
                 output_folder,
                 verbose=0):
    """

    :param candidate_ble_info:
    :param annotation_task:
    :param output_folder:
    """
    list_of_lists = []
    headers = ['Node ID', 'Delta subevents', 'Delta participants']

    for node in candidate_ble_info['subevents']: # ugly hack to get iterable of relevant nodes

        one_row = [node,
                   candidate_ble_info['subevents'][node]['delta'],
                   candidate_ble_info['participants'][node]['delta'],
                   ]
        list_of_lists.append(one_row)

    df = pd.DataFrame(list_of_lists, columns=headers)

    df = df.sort_values('Delta subevents', ascending=False)

    excel_path = f'{output_folder}/ble_delta.xlsx'
    df.to_excel(excel_path, index=False)

    tex_path = f'{output_folder}/ble_delta.tex'
    df.to_latex(tex_path, index=False)

    if verbose:
        print()
        print('saved BLE delta table to')
        print(excel_path)
        print(tex_path)


