import os
import json
from collections import Counter, defaultdict
import pandas as pd

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
            string_value = values[index]
            edge = id_to_edge[id_] # edges is (parent, child)

            if string_value in {'dk', 'ns'}:
                value = string_value
            elif string_value in {'1', '2', '3', '4', '5', '6', '7'}:
                value = int(string_value)
            else:
                raise Exception(f'provided annotation {string_value} for id {id_} is not valid. Please inspect.')

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





