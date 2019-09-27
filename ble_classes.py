import networkx as nx
import nltk
from collections import defaultdict
import itertools
import statistics
import pandas


def update_one_dict_with_another(original_d, new_d, verbose=0):
    """

    :param original_d:
    :param new_d:
    :return:
    """
    changed_keys = set()
    for key, value in new_d.items():
        if key in original_d:
            old_value = original_d[key]
            new_value = new_d[key]

            if new_value != old_value:
                original_d[key] = new_value
                if verbose >= 3:
                    print(f'changed {old_value} to {new_value} for key {key}')
                changed_keys.add(key)

    if verbose >= 2:
        print(f'keys changed: {changed_keys}')


#update_one_dict_with_another({'a': 1, 'b': 2}, {'a': 2, 'b': 2}, verbose=3)

def get_parents2children(nodes, g):
    parent2children = defaultdict(set)
    for node_one, node_two in itertools.combinations(nodes, 2):
        if nx.has_path(g, node_one, node_two):
            parent2children[node_one].add(node_two)
        if nx.has_path(g, node_two, node_one):
            parent2children[node_two].add(node_one)
    return parent2children


def min_mean_max(values, round_to=1):

    if values:
        minimum = min(values)
        maximum = max(values)
        mean = statistics.mean(values)
    else:
        minimum = 0
        mean = 0
        maximum = 0
    return minimum, round(mean, round_to), maximum


def obtain_local_maxima(list_of_keys, key2freq):
    """
    a local maximum:
    -previous key and key after it have a lower frequency

    :param list list_of_keys: list of keys
    :param key2freq:

    :return: list
    :return: list of local maxima
    """
    local_maxima = []
    local_maximum_score = 0
    for before, core, after in nltk.trigrams(list_of_keys):

        if all([key2freq.get(core, 0) > key2freq.get(before, 0),
                key2freq.get(core, 0) > key2freq.get(after, 0)]):
            local_maxima.append(core)

    freq_info = []
    for item in list_of_keys:
        freq_info.append((item, key2freq.get(item, 0)))

    if local_maxima:
        local_maximum_score = key2freq.get(local_maxima[0], 0)

    return local_maxima, local_maximum_score



list_of_keys = ['a', 'b', 'c', 'd', 'e', 'f']
key2freq = {'a' : 1, 'b' : 2, 'c': 1, 'd': 4, 'e': 1, 'f': 6}
result = obtain_local_maxima(list_of_keys, key2freq)
assert result == (['b', 'd'], 2)



class BLECollection:
    """
    Basic Level Event collection

    :param g: a networkx directed graph.
    the directed relation depends on the resource used, e.g.,
    -Wikidata: we have used to "subclass of" relation
    -WordNet: we would use the hypernym relation
    ...
    Each node in the graph must have the following properties:
    a) 'label'
    b) 'occurrence_frequency':
    -Wikidata: how many incidents are tagged with a certain event type
    -WordNet: how many times has a synset been annotated?
    c) 'features': list of features
    -Wikidata: list of properties for an event type
    -WordNet: list of semantic relations

    :param str root_node: the selected root_node
    only this root_node and all of its descendants will be used
    :param str weight_property: supported: 'occurrence_frequency' | 'features'
    :param int subsumer_threshold: how many nodes should there be below
    the BLE? How many should it minimally subsume?


    """
    def __init__(self,
                 g,
                 root_node,
                 weight_property,
                 subsumer_threshold,
                 root_zero=True,
                 verbose=0):
        self.root_node = root_node
        self.root_zero = root_zero
        self.weight_property = weight_property
        self.subsumer_threshold = subsumer_threshold
        self.verbose = verbose

        self.g = self.get_subgraph(g)
        self.validate()

        self.leaf_nodes = self.get_leaf_nodes()

        self.leaf_nodes = set(list(self.leaf_nodes)[:1000])
        self.node_id2node_obj = self.load_node_objs(self.leaf_nodes)

        self.node_id2bl_obj = self.compute_bls(source_node_objs=self.node_id2node_obj.values(),
                                               candidate_bles=set(self.g.nodes()))

        self.remove_overlapping_bls()

        # TODO: create bl2bl_obj and use that in stats

        self.stats = self.get_stats()

    def __str__(self):
        info = ['\nSETTINGS:']

        attrs = ['root_zero', 'weight_property', 'subsumer_threshold']
        for attr in attrs:
            info.append(f'setting {attr}: {getattr(self, attr)}')

        info.append('\nSTATS:')
        for key, value in self.stats.items():
            info.append(f'{key}: {value}')

        info.append('\n')

        return '\n'.join(info)

    def get_stats(self):
        ble_objs = {bl_obj
                    for bl_obj in self.node_id2bl_obj.values()
                    if bl_obj is not None}
        info = {
            '# of unique bles': len(ble_objs),
        }

        for attr in ['weight_value',
                     'node_depth',
                     'num_descendants',
                     'cumulative_weight'
                     ]:
            values = [getattr(ble_obj, attr)
                      for ble_obj in ble_objs]
            minimum, mean, maximum = min_mean_max(values)

            info[attr] = f'mean: {mean} (min: {minimum}, max: {maximum})'
        return info


    def print_bles(self, min_cumulative_freq=0):

        attrs = ['weight_value',
                 'node_depth',
                 'num_descendants',
                 'cumulative_weight']

        list_of_lists = []
        headers = ['Node label'] + attrs
        covered = set()
        for bl_obj in self.node_id2bl_obj.values():

            if bl_obj is None:
                continue

            if bl_obj.id_ in covered:
                continue

            covered.add(bl_obj.id_)

            values = [getattr(bl_obj, attr)
                      for attr in attrs]
            values.insert(0, f'{bl_obj.label} ({bl_obj.id_})')
            if values[-1] >= min_cumulative_freq:
                list_of_lists.append(values)

        df = pandas.DataFrame(list_of_lists, columns=headers)

        print(df)

    def validate(self):
        supported = {'occurrence_frequency', 'num_features'}
        assert self.weight_property in supported, f'weight property {self.weight_property} is not part of supported: {supported}'
        assert type(self.g) == nx.classes.digraph.DiGraph, f'provided graph must be of type nx.classes.digraph.DiGraph, got {type(self.g)}'

        needed_attributes = ['label', 'occurrence_frequency', 'features']
        for node in self.g.nodes():
            node_obj = self.g.nodes[node]
            for needed_attribute in needed_attributes:
                assert needed_attribute in node_obj, f'attribute {needed_attribute} missing from node {node}'

    def get_subgraph(self, g):
        """
        :return: networkx directed graph with only self.root_node
        and its descendants
        """
        assert g.has_node(self.root_node), f'node {self.root_node} not found in directed graph'

        top_descendants = nx.descendants(g, self.root_node)
        top_descendants.add(self.root_node)

        sub_g = nx.subgraph(g, top_descendants)

        if self.root_zero:
            before = sub_g.nodes[self.root_node][self.weight_property]
            sub_g.nodes[self.root_node][self.weight_property] = 0
            after = sub_g.nodes[self.root_node][self.weight_property]

            if self.verbose:
                print()
                print(f'changed {self.weight_property} of ROOT NODE from {before} to {after}')

        if self.verbose:
            print()
            print(f'found {len(top_descendants) - 1} descendants of top node {self.root_node}')

            print(nx.info(sub_g))

        return sub_g

    def get_leaf_nodes(self):
        leaf_nodes = set()
        for node in self.g.nodes():
            descendants = nx.descendants(self.g, node)
            if not descendants:
                leaf_nodes.add(node)

        if self.verbose:
            print()
            print(f'found {len(leaf_nodes)} leaf node(s)')

        return leaf_nodes


    def load_node_objs(self, node_ids):
        node2node_obj = {}

        for node_id in node_ids:
            node_info = self.g.nodes[node_id]
            node_obj = Node(id_=node_id,
                            label=node_info['label'],
                            occurrence_frequency=node_info['occurrence_frequency'],
                            features=node_info['features'])

            node2node_obj[node_id] = node_obj
            node_obj.set_paths_to_topnode(self.g, self.root_node)

        return node2node_obj

    def compute_bls(self, source_node_objs, candidate_bles):
        """

        :param list source_node_ids: list of Node objects for which you want to compute BLs
        :param set candidate_bles: set of ids which are possible candidate_bles
        if you add all node_ids, all node_ids are candidate BLs
        if you add a subset of all nodes, only those can be BLs
        :return:
        """
        node_id2bl_obj = {}

        for node_obj in source_node_objs:

            node_obj.set_chosen_path_and_local_maxima(self.g,
                                                      self.weight_property)


            bl = None

            for local_maximum in node_obj.chosen_local_maxima:
                the_descendants = nx.descendants(self.g, local_maximum)

                if len(the_descendants) >= self.subsumer_threshold:
                    bl = local_maximum
                    break

            # update: node has ble
            if bl not in candidate_bles:
                if self.verbose >= 3:
                    print(f'bl {bl} for {node_obj.id_} not accepted since not in candidate bls')
                bl = None


            if bl is None:
                node_id2bl_obj[node_obj.id_] = None
            else:
                # add ble for node that was not there before
                bl_info = self.g.nodes[bl]
                depth = len(nx.shortest_path(self.g, self.root_node, bl))

                descendant_cumulative_weight = sum([self.g.nodes[descendant][self.weight_property]
                                                    for descendant in the_descendants])
                cumulative_weight = descendant_cumulative_weight + bl_info[self.weight_property]

                bl_obj = BL(id_=bl,
                            label=bl_info['label'],
                            node_depth=depth,
                            weight_value=bl_info[self.weight_property],
                            descendants=the_descendants,
                            cumulative_weight=cumulative_weight)

                node_id2bl_obj[node_obj.id_] = bl_obj


        return node_id2bl_obj



    def remove_overlapping_bls(self):

        the_bles = {bl_obj.id_
                    for bl_obj in self.node_id2bl_obj.values()
                    if bl_obj is not None}
        parent2children = get_parents2children(the_bles, self.g)

        if self.verbose >= 2:
            print()
            print(f'STARTED REMOVING OVERLAPPING BLS there are now {len(the_bles)}')
            print(parent2children)

        while parent2children:

            # TODO: use more dominant BLs instead of parent one

            num_removed = 0
            # remove parent BLs
            for parent_bl, children_bls in parent2children.items():

                # set freq to zero
                self.g.nodes[parent_bl][self.weight_property] = 0
                if self.verbose >= 4:
                    print(f'set {parent_bl} to zero')

                # recompute BLs
                the_candidate_bles = nx.descendants(self.g, parent_bl)

                # determine nodes and candidate bles for which you want to recompute bls
                node_objs = []
                parent_descendants = nx.descendants(self.g, parent_bl)
                for node_id, bl_obj in self.node_id2bl_obj.items():
                    if node_id in parent_descendants:
                        node_objs.append(self.node_id2node_obj[node_id])

                local_nodeid2bl_obj = self.compute_bls(source_node_objs=node_objs,
                                                       candidate_bles=the_candidate_bles)

                # update global node_id2bl_obj
                update_one_dict_with_another(self.node_id2bl_obj, local_nodeid2bl_obj, verbose=self.verbose)

            the_bles = {bl_obj.id_
                        for bl_obj in self.node_id2bl_obj.values()
                        if bl_obj is not None}

            parent2children = get_parents2children(the_bles, self.g)



class BL:
    """
    instance of Basic Level
    """
    def __init__(self,
                 id_,
                 label,
                 node_depth,
                 weight_value, # can be either num_features or occurrence_freq
                 descendants,
                 cumulative_weight):
        self.id_ = id_
        self.label = label
        self.node_depth = node_depth
        self.weight_value = weight_value
        self.descendants = descendants
        self.num_descendants = len(self.descendants)
        self.cumulative_weight = cumulative_weight

    def __str__(self):
        attrs = ['id_', 'label', 'node_depth',
                 'weight_value',
                 'num_descendants']

        info = []
        for attr in attrs:
            info.append(f'KEY: {attr}: VALUE: {getattr(self, attr)}')

        return '\n'.join(info)


class Node:
    """
    instance of an event type

    :param str id_: event type identifier
    -Wikidata: wd:Q etc.
    :param str label: label
    -Wikidata: event type label
    :param int occurrence_frequency:
    -Wikidata: how many incidents are tagged with a certain event type
    -WordNet: how many times has a synset been annotated?
    :param list features: a list of features
    -Wikidata: properties of this type
    -WordNet: semantic relations of synset
    """
    def __init__(self, id_, label, occurrence_frequency, features, verbose=0):
        self.id_ = id_
        self.label = label
        self.occurrence_frequency = occurrence_frequency
        self.features = features
        self.num_features = len(features)

        self.path_debug_information = [] # debug information after choosing one path if there are multiple (available after calling self.set_chosen_path_and_local_maxima())
        self.verbose = verbose


    def __str__(self):
        attrs = ['id_', 'label', 'occurrence_frequency',
                 'num_features',
                 'paths_to_topnode',
                 'path_debug_information']

        info = []
        for attr in attrs:
            info.append(f'KEY: {attr}: VALUE: {getattr(self, attr)}')

        return '\n'.join(info)

    def set_paths_to_topnode(self, g, top_node):
        """

        :param g:
        :return:
        """
        paths = list(nx.all_simple_paths(g, top_node, self.id_))

        assert len(paths) >= 1, f'no path found from {self.id_} to top_node {top_node}'

        for path in paths:
            path.reverse()
        self.paths_to_topnode = paths


    def set_chosen_path_and_local_maxima(self, g, weight_attribute):
        """

        :return:
        """
        self.path_debug_information = []

        self.chosen_path_to_top = []
        self.chosen_local_maxima = []

        selected_path = None

        max_local_maximum_score = 0

        assert hasattr(self, 'paths_to_topnode'), f'please call self.set_paths_to_topnode first'

        for index, path in enumerate(self.paths_to_topnode):

            node2freq = {node: g.nodes[node][weight_attribute]
                         for node in path}

            local_maxima, local_maximum_score = obtain_local_maxima(path, node2freq)

            if local_maximum_score > max_local_maximum_score:
                self.chosen_path_to_top = path
                self.chosen_local_maxima = local_maxima
                selected_path = index
                max_local_maximum_score = local_maximum_score

            self.path_debug_information.append((f'INDEX: {index}', path, local_maxima, local_maximum_score))

        self.path_debug_information.append(f'SELECTED: {selected_path}')


if __name__ == '__main__':


    nodes = {
        0: {'label': 'one', 'occurrence_frequency': 0, 'features': [], 'num_features': 0},
        1 : {'label': 'one', 'occurrence_frequency' : 1, 'features' : [], 'num_features': 0},
        2 : {'label': 'two', 'occurrence_frequency': 10, 'features': [], 'num_features': 0},
        3 : {'label': 'three', 'occurrence_frequency': 5, 'features': [], 'num_features': 0},
        4 : {'label': 'four', 'occurrence_frequency': 4, 'features': [], 'num_features': 0},
        5 : {'label': 'five', 'occurrence_frequency': 1, 'features': [], 'num_features': 0},
        6: {'label': 'six', 'occurrence_frequency': 4, 'features': [], 'num_features': 0},
        7: {'label': 'seven', 'occurrence_frequency': 1, 'features': [], 'num_features': 0},

    }

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

    ## THRESHOLD = 0
    # node 0 has node 2 as bl
    # node 7 has node 3 as bl
    # node 6 is no BL since node 3 has a higher occurrence_frequency than node 6
    # since 3 is a parent of 2, we remove it
    # we recompute BLs which means 6 becomes a BL


    selected_root_node = 5
    root_zero = True
    subsumer_threshold = 2
    verbose = 3


    g = nx.DiGraph()
    g.add_nodes_from(nodes.keys())
    nx.set_node_attributes(g, nodes)
    g.add_edges_from(edges)

    ble_coll_obj = BLECollection(g,
                                 root_node=selected_root_node,
                                 weight_property='occurrence_frequency',
                                 subsumer_threshold=subsumer_threshold,
                                 root_zero=root_zero,
                                 verbose=verbose)

    print(ble_coll_obj)
    ble_coll_obj.print_bles()


