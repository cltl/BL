import os
import json
from collections import Counter, defaultdict
import pandas as pd
import networkx as nx
import statistics

from sklearn.metrics import cohen_kappa_score

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


def obtain_kappa_score(output_folder, users, annotation_task):
    """

    :param output_folder:
    :param annotation_task:
    :return:
    """
    user_one, user_two = users

    path = os.path.join(output_folder, f'{annotation_task}_{user_one}.json')
    with open(path) as infile:
        info_user_one = json.load(infile)

    path = os.path.join(output_folder, f'{annotation_task}_{user_two}.json')
    with open(path) as infile:
        info_user_two = json.load(infile)

    assert set(info_user_one) == set(info_user_two)

    labels_user_one = []
    labels_user_two = []
    for key in info_user_one:
        labels_user_one.append(info_user_one[key])
        labels_user_two.append(info_user_two[key])

    kappa = cohen_kappa_score(y1=labels_user_one, y2=labels_user_two)

    return kappa

def compute_agreement(edge_to_user_to_task_to_value,
                      annotation_task,
                      output_folder,
                      verbose=0):
    """
    create a table in which the user agreement for a particular task is shown

    """
    category_to_edges = defaultdict(list)

    filtered_user_to_edge_to_value = defaultdict(dict)
    num_cat_other = 0

    for edge, user_to_task_to_value in edge_to_user_to_task_to_value.items():

        user_to_value = {user: task_to_value[annotation_task]
                         for user, task_to_value in user_to_task_to_value.items()}
        values = list(user_to_value.values())

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

        if category == "other":
            num_cat_other += 1
            continue

        category_to_edges[category].append(edge)

        for user, value in user_to_value.items():
            edge_string = '---'.join([id_ for id_ in edge])
            filtered_user_to_edge_to_value[user][edge_string] = value

    num_annotations = []
    for user, annotations in filtered_user_to_edge_to_value.items():
        num_annotations.append(len(annotations))
    assert len(set(num_annotations)) == 1, f'this set should only have one value: {num_annotations}'

    for user, annotations in filtered_user_to_edge_to_value.items():
        json_path = os.path.join(output_folder, f'{annotation_task}_{user}.json')
        with open(json_path, 'w') as outfile:
            json.dump(annotations, outfile)

    if verbose:
        print()
        print(f'number of items in category "other": {num_cat_other}')
        print('i.e., one annotator specified an integer and the other dk or ns')

    # create table
    list_of_lists = []
    headers = ['Delta between annotations', 'Number of items']

    for category, edges in category_to_edges.items():
        one_row = [category, len(edges)]
        list_of_lists.append(one_row)

    df = pd.DataFrame(list_of_lists, columns=headers)
    df = df.sort_values('Delta between annotations')

    # cumulative relative frequency
    num_items = sum(df['Number of items'])
    cum_rel_freq_values = []
    cum_rel_freq = 0

    for index, row in df.iterrows():
        rel_freq = 100 * (row['Number of items'] / num_items)
        cum_rel_freq += rel_freq
        cum_rel_freq_values.append(cum_rel_freq)

    df['Cumulative Rel Freq'] = cum_rel_freq_values

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
        children_edges_to_value = dict()
        for children_edge in children_edges:
            child_edge_avg = get_average_edge_value(g, children_edge, annotation_task, users, verbose=verbose)
            if child_edge_avg is not None:
                children_avgs.append(child_edge_avg)
                children_edges_to_value[children_edge] = child_edge_avg

        parent_avgs = []
        parent_edges_to_value = dict()
        for parent_edge in parent_edges:
            parent_edge_avg = get_average_edge_value(g, parent_edge, annotation_task, users, verbose=verbose)
            if parent_edge_avg is not None:
                parent_avgs.append(parent_edge_avg)
                parent_edges_to_value[parent_edge] = parent_edge_avg

        if any([not children_avgs,
                not parent_avgs]):
            continue

        children_value = sum(children_avgs) / len(children_avgs)
        parent_value = sum(parent_avgs) / len(parent_avgs)
        delta = children_value - parent_value
        result = {
            'children': children_value,
            'children_edges_to_value' : children_edges_to_value,
            'parents': parent_value,
            'parents_edges_to_value' : parent_edges_to_value,
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
                 node_to_depth,
                 output_folder,
                 verbose=0):
    """

    :param candidate_ble_info:
    :param annotation_task:
    :param output_folder:
    """
    list_of_lists = []
    headers = ['Node ID', 'Node Depth', 'Delta subevents', 'Delta participants']

    for node in candidate_ble_info['subevents']: # ugly hack to get iterable of relevant nodes

        delta_subevents = candidate_ble_info['subevents'][node]['delta']
        delta_participants = candidate_ble_info['participants'][node]['delta']
        one_row = [node,
                   node_to_depth[node],
                   round(delta_subevents, 1),
                   round(delta_participants, 1),
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

    return df


def analyze_df(df,
               turning_point,
               annotation_task,
               verbose=0):
    """

    :param df:
    :return:
    """

    low = []
    high = []

    for index, row in df.iterrows():

        task_value = row[f'Delta {annotation_task}']
        depth = row['Node Depth']

        if task_value >= turning_point:
            high.append(depth)
        else:
            low.append(depth)

    high_avg_depth = statistics.mean(high)
    low_avg_depth = statistics.mean(low)

    if verbose >= 1:
        print()
        print('turning point', turning_point)
        print('on or above turning point', len(high))
        print('below turning point', len(low))
        print('average depth')
        print('high', round(high_avg_depth,2))
        print('low', round(low_avg_depth,2))
        print('high distribution', sorted(Counter(high).items()))
        print('high standard deviation', statistics.stdev(high))
        print('low distribution', sorted(Counter(low).items()))
        print('low standard deviation', statistics.stdev(low))



def create_dot_of_ble_candidate(ble_candidate_info,
                                ev_coll_obj,
                                output_path=None,
                                verbose=0):
    """

    :param dict ble_candidate_info: see output determine_candidate_basic_levels
    {'children': 5.25,
      'children_edges_to_value': {('Q3270632', 'Q4582333'): 6.5,
       ('Q3270632', 'Q1152547'): 4.0},
      'parents': 5.5,
      'parents_edges_to_value': {('Q18608583', 'Q3270632'): 4.5,
       ('Q1079023', 'Q3270632'): 6.5},
      'delta': -0.25}}
    """

    g = nx.DiGraph()

    keys = ['children_edges_to_value',
            'parents_edges_to_value']

    nodes = set()
    for key in keys:
        for (u, v) in ble_candidate_info[key]:
            nodes.update((u, v))

    for node in nodes:
        uri = f'http://www.wikidata.org/entity/{node}'
        ev_obj = ev_coll_obj.event_type_id_to_event_type_obj[uri]
        g.add_node(node, label=ev_obj.label_to_show)

    for key in keys:
        edges = ble_candidate_info[key]
        for (u, v), weight in edges.items():
            g.add_edge(u, v, label=weight)

    if output_path is not None:
        p = nx.drawing.nx_pydot.to_pydot(g)
        p.write_png(output_path)

        if verbose >= 3:
            print()
            print(f'written output to {output_path}')




