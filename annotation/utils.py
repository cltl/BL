from collections import defaultdict
import operator
import networkx as nx
import itertools
import pandas


def divide_work(items,
                annotators,
                num_annotations_per_item,
                ignore=set(),
                verbose=0):
    items = [item
             for item in items
             if item not in ignore]

    workers = list(annotators)
    num_annotations = 3
    queue = sorted([item
                    for item in items
                    for _ in range(num_annotations)
                    ])

    qid2freq = defaultdict(int)
    annotator_to_items = defaultdict(set)

    for worker, task in zip(itertools.cycle(workers), queue):
        annotator_to_items[worker].add(task)
        qid2freq[task] += 1

    for q_id, freq in qid2freq.items():
        assert freq == num_annotations_per_item, f'{q_id} has freq {freq}'

    if verbose:
        print()
        print(f'number of items: {len(items)}')
        print(f'annotators: {annotators}')
        print(f'number of annotations per item: {num_annotations_per_item}')
        for annotator, items in annotator_to_items.items():
            print(annotator, len(items))

    return annotator_to_items


def target_df(g, min_freq, min_descendants, min_num_children,
              forbidden_in_path):
    list_of_lists = []
    headers = ['ID',
               'paths_to_event_node',
               'instance_freq',
               'parents',
               'children',
               'num_children',
               'chosen_children',
               'num_descendants', ]

    for node_id in g.nodes():

        instance_freq = g.nodes[node_id]['occurrence_frequency']
        if instance_freq < min_freq:
            continue

        descendants = nx.descendants(g, node_id)
        num_descendants = len(descendants)

        if num_descendants < min_descendants:
            continue

        children = list(g.successors(node_id))
        num_children = len(children)

        if num_children < min_num_children:
            continue

        parents = list(g.predecessors(node_id))

        paths_to_top = list(nx.all_simple_paths(g,
                                            'wd:Q1656682',
                                            node_id))

        if not paths_to_top:
            continue

        to_add = True
        for path in paths_to_top:
            for node in path:
                if node in forbidden_in_path:
                    to_add = False

        if not to_add:
            continue

        child2freq = {child: g.nodes[child]['occurrence_frequency']
                      for child in children}

        chosen_children = most_frequent_keys(child2freq, 3)

        one_row = [node_id,
                   paths_to_top,
                   instance_freq,
                   parents,
                   children,
                   num_children,
                   chosen_children,
                   num_descendants]

        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)
    return df

def get_paths(bl_coll_obj,
              g,
              min_length=0,
              min_freq=0,
              at_least=0,
              verbose=0):

    all_paths = []
    edge2freq = defaultdict(int)
    edge2children = defaultdict(set)

    for node_id, node_obj in bl_coll_obj.node_id2node_obj.items():

        for path in node_obj.paths_to_topnode:

            if len(path) < min_length:
                continue

            if not all([g.nodes[node]['occurrence_frequency'] >= min_freq
                        for node in path]):
                continue

            if not any([g.nodes[node]['occurrence_frequency'] >= at_least
                        for node in path[:-1]]):
                continue


            all_paths.append(path)

            for source, target in zip(path, path[1:]):
                edge2freq[(source, target)] += 1
                edge2children[target].add(source)

    if verbose:
        print()
        print(f'min length: {min_length}')
        print(f'min freq: {min_freq}')
        print(len(all_paths), len(edge2freq))

        index = 0
        total = sum(edge2freq.values())
        subtotal = 0
        for (source, target), value in sorted(edge2freq.items(),
                                 key=operator.itemgetter(1),
                                 reverse=True):
            index += 1
            subtotal += value



    return all_paths, edge2freq, edge2children


def most_frequent_keys(a_dict, top_n):
    items = sorted(a_dict.items(),
                   key=operator.itemgetter(1),
                   reverse=True)

    chosen_keys = set()
    for key, value in items[:top_n]:
        chosen_keys.add(key)

    return chosen_keys


example = {'a': 2, 'b': 3, 'c': 3, 'd': 1}
assert most_frequent_keys(example, 3) == {'a', 'b', 'c'}


def get_parents2children(nodes, g):
    parent2children = defaultdict(set)
    for node_one, node_two in itertools.combinations(nodes, 2):
        if nx.has_path(g, node_one, node_two):
            parent2children[node_one].add(node_two)
        if nx.has_path(g, node_two, node_one):
            parent2children[node_two].add(node_one)
    return parent2children