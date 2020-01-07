import json
import pickle
from collections import defaultdict

import networkx as nx

from graph_utils import get_leaf_nodes
from wd_utils import from_short_uri_to_full_uri
from stats_utils import show_top_n, get_sample

# TODO: total cue validity
# TODO: stats
#   - which ones to show?
# TODO: think about new ways of creating the experiment
#   - dive back into the literature

class EventTypeCollection:
    """
    represents a Wikidata event type collection

    inspect wd_utils.QUERIES for the precise queries passed to the Wikidata sparql api

    :param str path_subclass_of_rels: path to 'subclass_of.json' (result of query 'subclass_of' in QUERIES)
    :param str path_instance_of_rels: path to 'instance_of.json' (result of query 'instance_of' in QUERIES)
    :param str path_inc_to_labels: path to 'inc_to_labels.json' (result of query 'inc_to_labels' in QUERIES)
    :param str path_inc_to_props: path to 'inc_to_props.json' (result of query 'inc_to_props' in QUERIES)
    :param str path_event_type_to_labels: path to 'event_type_to_labels.json' (result of query 'event_type_to_labels' in QUERIES)
    :param str path_prop_to_labels: path to 'prop_to_labels.json' (result of query 'prop_to_labels' in QUERIES)

    :param str root_node: the node used as root node in the directed graph, e.g.,
    http://www.wikidata.org/entity/Q1656682 for event

    :param set needed_properties: if provided, an Incident object is only created if minimally
    those properties are present for the incident, e.g., {'http://www.wikidata.org/prop/direct/P17'}
    :param set properties_to_ignore: if provided, these properties will be ignored,
    i.e., no Property object will be created, e.g., {'http://www.wikidata.org/prop/direct/P31', 'http://www.wikidata.org/prop/direct/P279'}
    :param int min_leaf_incident_freq: the minimum number of incident that a leaf node in the directed has to have
    to be accepted in the graph. If this is set to 1 or higher, all leaf nodes will be removed until there are
    only leaf nodes with the minimum number of allowed incidents
    """
    def __init__(self,
                 path_subclass_of_rels,
                 path_instance_of_rels,
                 path_inc_to_labels,
                 path_inc_to_props,
                 path_event_type_to_labels,
                 path_prop_to_labels,
                 root_node,
                 needed_properties=set(),
                 properties_to_ignore=set(),
                 min_leaf_incident_freq=0,
                 verbose=0):
        self.verbose = verbose

        self.prop_id_to_prop_obj = self.get_property_to_property_obj(path_prop_to_labels=path_prop_to_labels, properties_to_ignore=properties_to_ignore)
        self.inc_id_to_inc_obj = self.get_inc_to_inc_obj(path_inc_to_labels=path_inc_to_labels,
                                                         path_inc_to_props=path_inc_to_props,
                                                         needed_properties=needed_properties)
        self.event_type_id_to_event_type_obj = self.get_event_type_to_eventtype_obj(path_event_type_to_labels=path_event_type_to_labels)
        self.update_event_types_with_incidents(path_instance_of_rels=path_instance_of_rels)

        self.g, \
        self.leaf_nodes = self.create_directed_graph(path_subclass_of_rels,
                                                     root_node,
                                                     min_leaf_incident_freq)

        # restrict to only event subgraph
        self.event_type_id_to_event_type_obj = {event_uri : event_type_obj
                                                for event_uri, event_type_obj in self.event_type_id_to_event_type_obj.items()
                                                if event_type_obj.prefix_uri in self.g}

        self.prop_to_freq, \
        self.evtype_and_prop_to_freq = self.compute_prop_freq()
        self.update_cue_validities()

        for event_type_obj in self.event_type_id_to_event_type_obj.values():
            event_type_obj.set_children(self.g)
            event_type_obj.set_parents(self.g)
            event_type_obj.set_subsumers(self.g)
            event_type_obj.set_parent_to_siblings(self.g)

        self.stats = self.compute_stats(root_node, min_leaf_incident_freq, needed_properties)


    def __str__(self):
        info = []

        for stat, value in self.stats.items():
            info.append(f'STATISTIC {stat}: value {value}')

        return '\n'.join(info)

    def get_property_to_property_obj(self, path_prop_to_labels, properties_to_ignore):
        """
        load mapping from property id (full uri) -> instance of class Property
        """
        with open(path_prop_to_labels) as infile:
            prop_to_label_rels = json.load(infile)

        prop_to_labels = defaultdict(set)
        for prop_uri, label in prop_to_label_rels:
            prop_to_labels[prop_uri].add(label)

        prop_id_to_prop_obj = dict()
        for prop_uri, labels in prop_to_labels.items():

            if prop_uri in properties_to_ignore:
                if self.verbose >= 2:
                    print(f'ignored Property {prop_uri}')
                continue

            prop_uri = prop_uri.replace('http://www.wikidata.org/entity/',
                                        'http://www.wikidata.org/prop/direct/')

            label = list(labels)[0]
            title_id = prop_uri.split('/')[-1]


            prop_obj = Property(title_labels={'en' : label},
                                title_id=title_id,
                                full_uri=prop_uri,
                                prefix_uri=f'wdt:{title_id}')

            prop_id_to_prop_obj[prop_uri] = prop_obj

        if self.verbose >= 1:
            print()
            print(f'found {len(prop_id_to_prop_obj)} different properties')

        return prop_id_to_prop_obj


    def get_inc_to_inc_obj(self, path_inc_to_labels, path_inc_to_props, needed_properties):
        """
        load Incident id (full_uri) to instance of Incident class
        """
        with open(path_inc_to_labels) as infile:
            inc_to_label_rels = json.load(infile)

            inc_to_lang_to_label = defaultdict(dict)
            for inc_uri, (lang, label) in inc_to_label_rels:
                inc_to_lang_to_label[inc_uri][lang] = label

        with open(path_inc_to_props) as infile:
            inc_to_prop_rels = json.load(infile)

            inc_to_props = defaultdict(set)
            for inc_uri, prop_uri in inc_to_prop_rels:
                inc_to_props[inc_uri].add(prop_uri)


        inc_uri_to_inc_obj = dict()

        for inc_uri, labels in inc_to_lang_to_label.items():

            props = inc_to_props[inc_uri]
            title_id = inc_uri.split('/')[-1]

            # check if all mandatory properties are present
            skip = False
            for needed_prop in needed_properties:
                if needed_prop not in props:
                    skip = True

            if skip:
                continue

            prop_objs = []
            for prop in props:
                if prop in self.prop_id_to_prop_obj:
                    prop_objs.append(self.prop_id_to_prop_obj[prop])

            inc_obj = Incident(title_labels=labels,
                               title_id=title_id,
                               full_uri=inc_uri,
                               prefix_uri=f'wd:{title_id}',
                               properties=prop_objs)

            inc_uri_to_inc_obj[inc_uri] = inc_obj

        if self.verbose >= 1:
            print()
            print(f'instantiated {len(inc_uri_to_inc_obj)} Incident instances')

        return inc_uri_to_inc_obj


    def get_event_type_to_eventtype_obj(self, path_event_type_to_labels):
        """
        create mapping event type uri -> instance of EventType object

        """
        with open(path_event_type_to_labels) as infile:
            event_type_to_label_rels = json.load(infile)

            event_type_to_labels = defaultdict(set)

            for event_type, label in event_type_to_label_rels:
                event_type_to_labels[event_type].add(label)


        event_type_uri_to_event_type_obj = dict()

        for event_type_uri, labels in event_type_to_labels.items():

            label = list(labels)[0]
            title_id = event_type_uri.split('/')[-1]

            event_type_obj = EventType(title_labels={'en' : label},
                                       title_id=title_id,
                                       full_uri=event_type_uri,
                                       prefix_uri=f'wd:{title_id}')

            event_type_uri_to_event_type_obj[event_type_uri] = event_type_obj


        if self.verbose >= 1:
            print()
            print(f'instantiated {len(event_type_uri_to_event_type_obj)} EventType objects')

        return event_type_uri_to_event_type_obj

    def update_event_types_with_incidents(self, path_instance_of_rels):
        """
        update attribute "incidents" of EventType objects with Incident objects
        """
        with open(path_instance_of_rels) as infile:
            instance_of_rels = json.load(infile)

            event_type_uri_to_incident_uri = defaultdict(set)

            for event_type_uri, incident_uri in instance_of_rels:
                event_type_uri_to_incident_uri[event_type_uri].add(incident_uri)

        if self.verbose >= 2:
            print()
            print(f'found inc_wd_uris for {len(event_type_uri_to_incident_uri)} event types')

        num_inc_uris_added = []
        for event_type_uri, incident_uris in event_type_uri_to_incident_uri.items():

            event_type_obj = self.event_type_id_to_event_type_obj.get(event_type_uri, None)

            if event_type_obj is None:
                continue

            incident_uris = event_type_uri_to_incident_uri[event_type_uri]

            inc_objs = []
            for inc_uri in incident_uris:
                inc_obj = self.inc_id_to_inc_obj.get(inc_uri, None)
                if inc_obj is not None:
                    inc_objs.append(inc_obj)
            event_type_obj.incidents = inc_objs

            num_inc_uris_added.append(len(inc_objs))

        if self.verbose >= 1:
            print()
            print(f'updated incidents attributes for {len(num_inc_uris_added)} event types')

    def compute_prop_freq(self):
        prop_to_freq = defaultdict(int)
        evtype_and_prop_to_freq = defaultdict(int)

        for ev_type, ev_type_obj in self.event_type_id_to_event_type_obj.items():

            for unique_property, prop_freq in ev_type_obj.properties_aggregated.items():
                prop_to_freq[unique_property] += prop_freq
                evtype_and_prop_to_freq[(ev_type, unique_property)] += prop_freq

        return prop_to_freq, evtype_and_prop_to_freq

    def update_cue_validities(self):
        for ev_type, ev_type_obj in self.event_type_id_to_event_type_obj.items():
            ev_type_obj.set_cue_validities(self.prop_to_freq)

    def create_directed_graph(self,
                              path_subclass_of_rels,
                              root_node_id,
                              min_leaf_incident_freq):
        """"""
        with open(path_subclass_of_rels) as infile:
            set_of_relations = json.load(infile)

        relations = []
        for x, y in set_of_relations:  # x is subclass of y

            event_obj_x = self.event_type_id_to_event_type_obj.get(x, None)
            event_obj_y = self.event_type_id_to_event_type_obj.get(y, None)

            if all([event_obj_x,
                    event_obj_y]):
                relations.append((event_obj_y.prefix_uri,
                                  event_obj_x.prefix_uri))

        g = nx.DiGraph()
        g.add_edges_from(relations)

        if self.verbose >= 2:
            print()
            print(f'number of input relations: {len(relations)}')
            print(f'loaded full graph with {len(g.edges())} edges')
            print(nx.info(g))

        root_event_type_obj = self.event_type_id_to_event_type_obj[root_node_id]
        the_descendants = nx.descendants(g, root_event_type_obj.prefix_uri)

        if self.verbose >= 2:
            print()
            print(f'found {len(the_descendants)} for root node {root_event_type_obj.prefix_uri}')

        the_descendants.add(root_event_type_obj.prefix_uri)
        sub_g = g.subgraph(the_descendants).copy()

        node_attrs = {}
        for node in sub_g.nodes():
            full_uri = node.replace('wd:', 'http://www.wikidata.org/entity/')
            event_type_obj = self.event_type_id_to_event_type_obj[full_uri]
            label = event_type_obj.label_to_show
            freq = event_type_obj.num_incidents

            info = {
                'label': label,
                'occurrence_frequency': freq,
                'features': [],
                'num_features': []
            }
            node_attrs[node] = info

        nx.set_node_attributes(sub_g, node_attrs)

        if self.verbose >= 2:
            print()
            print(f'loaded subgraph graph with {len(sub_g.edges())} edges')
            print(nx.info(sub_g))
            print('top node:', root_event_type_obj.label_to_show)


        # clean graph from leaf nodes without incidents linked to them
        removed = set()
        leaf_nodes = {node
                      for node in get_leaf_nodes(sub_g, verbose=self.verbose)
                      if sub_g.nodes[node]['occurrence_frequency'] < min_leaf_incident_freq}

        while leaf_nodes:
            for leaf_node in leaf_nodes:
                sub_g.remove_node(leaf_node)
                removed.add(leaf_node)

            leaf_nodes = {node
                          for node in get_leaf_nodes(sub_g, verbose=self.verbose)
                          if sub_g.nodes[node]['occurrence_frequency'] < min_leaf_incident_freq}

        leaf_nodes = get_leaf_nodes(sub_g)

        if self.verbose >= 2:
            print()
            print(f'after removing leaf nodes: {len(sub_g.edges())} edges')
            print(nx.info(sub_g))
            print('top node:', root_event_type_obj.label_to_show)
            print(f'number of leaf nodes: {len(leaf_nodes)}')

        return sub_g, leaf_nodes


    def vizualize(self, root=None, from_to=None):
        """


        """
        assert [root, from_to].count(None) == 1, f'you can only provide root OR from_to'

    def create_hover_text(self,
                          ev_type_obj,
                          prop_stats='properties_aggregated',
                          ):
        """
`       create hover text for vizualizing EventType instance

        :param EventType ev_type_obj: instance of class EventType
        :param str prop_stats: properties_aggregated | cue_validities

        :rtype: str
        :return: the hover text
        """
        options = {'properties_aggregated', 'cue_validities'}
        assert prop_stats in options, f'please choose for prop_stats from {options}'

        info = []

        # Incident count per language
        info.append(f'\n### Number of incidents per language')
        lang_to_num_incidents = defaultdict(int)
        for inc_obj in ev_type_obj.incidents:
            for lang in inc_obj.title_labels.items():
                lang_to_num_incidents[lang] += 1

        for lang, num_incidents in lang_to_num_incidents.items():
            info.append(f'LANG: {lang}: {num_incidents} incidents')

        # Properties
        info.append(f'\n### Shared properties')
        prop_dict = getattr(ev_type_obj, prop_stats)
        prop_df = show_top_n(a_dict=prop_dict,
                             id_to_class_instance=self.event_type_id_to_event_type_obj,
                             label='label_to_show',
                             n=10)

        for index, row in prop_df.iterrows():
            info.append(f'{row["Item"]} - {row["Value"]}')

        # Examples
        info.append(f'\n### Sample of Incidents')
        inc_uris = [inc_obj.full_uri
                    for inc_obj in ev_type_obj.incidents]
        the_sample = get_sample(inc_uris, 5)

        for sample_inc_uri in the_sample:
            info.append(f'{sample_inc_uri}')

        return '\n'.join(info)

    def compute_stats(self, root_node, min_leaf_incident_freq, needed_properties):
        stats = {}

        num_event_types = len(self.event_type_id_to_event_type_obj)
        stats['root_node'] = root_node
        stats['minimum # of incidents for event type leaf node'] = min_leaf_incident_freq
        stats['required properties for incident'] = needed_properties
        stats['num_event_types'] = num_event_types
        stats['num_leaf_nodes'] = len(self.leaf_nodes)

        inc_uris = {inc_obj.full_uri
                    for event_type_obj in self.event_type_id_to_event_type_obj.values()
                    for inc_obj in event_type_obj.incidents}
        stats['num_inc_uris'] = len(inc_uris)

        stats['num_unique_properties'] = len(self.prop_to_freq)

        return stats

    def pickle_it(self, output_path):
        with open(output_path, 'wb') as outfile:
            pickle.dump(self, outfile)

        if self.verbose:
            print()
            print(f'saved EventTypeCollection to {output_path}')




class EventType():
    """
    represents a Wikidata event type, e.g.,

    title_label={'en' : 'election'}
    title_id='Q40231',
    full_uri='http://www.wikidata.org/entity/Q40231',
    prefix_uri='wd:Q40231',
    """
    def __init__(self,
                 title_labels,
                 title_id,
                 full_uri,
                 prefix_uri,
                 ):
        self.title_labels = title_labels
        self.label_to_show = self.set_label_to_show()
        self.title_id = title_id
        self.full_uri = full_uri
        self.prefix_uri = prefix_uri
        self.incidents = []

        self.cue_validities = None      # is updated by method set_cue_validities
        self.children = None            # is updated by set_children
        self.parents = None             # is updated by set_parents
        self.subsumers = None           # is updated by set_subsumers
        self.parent_to_siblings = None  # is updated by set_parent_to_siblings

    def __str__(self):
        info = ['Information about EventType:']

        attrs = ['title_labels',
                 'title_id',
                 'full_uri',
                 'prefix_uri']
        for attr in attrs:
            info.append(f'ATTR {attr} has value: {getattr(self, attr)}')

        count_attrs = ['incidents',
                       'children',
                       'parents',
                       'subsumers']

        for count_attr in count_attrs:
            value = getattr(self, count_attr)
            info.append(f'ATTR {count_attr} has {len(value)} items')


        for parent, siblings in self.parent_to_siblings.items():
            info.append(f'{len(siblings)} siblings from parent {parent}')

        return '\n'.join(info)

    def set_label_to_show(self):
        label_to_show = self.title_labels.get('en', None)

        if label_to_show is None:
            for lang, label in self.title_labels.items():
                label_to_show = label
                break

        return label_to_show

    @property
    def num_incidents(self):
        return len(self.incidents)

    @num_incidents.setter
    def num_incidents(self, value):
        self._num_incidents = value

    @property
    def properties_aggregated(self):
        unique_prop_to_freq = defaultdict(int)
        for inc_obj in self.incidents:
            for unique_property in inc_obj.unique_properties:
                unique_prop_to_freq[unique_property] += 1
        return unique_prop_to_freq

    @properties_aggregated.setter
    def properties_aggregated(self, value):
        self._properties_aggregated = value

    def set_cue_validities(self, wd_prop_to_freq):
        self.cue_validities = dict()
        for unique_property, freq_in_event_type in self.properties_aggregated.items():
            wd_prop_freq = wd_prop_to_freq[unique_property]
            cue_validity = freq_in_event_type / wd_prop_freq
            self.cue_validities[unique_property] = cue_validity


    def set_children(self, g):
        children = g.successors(self.prefix_uri)
        self.children = {from_short_uri_to_full_uri(child)
                         for child in children}

    def set_parents(self, g):
        parents = g.predecessors(self.prefix_uri)
        self.parents = {from_short_uri_to_full_uri(parent)
                        for parent in parents}


    def set_subsumers(self, g):
        subsumers = nx.descendants(g, self.prefix_uri)
        self.subsumers = {from_short_uri_to_full_uri(subsumer)
                          for subsumer in subsumers}

    def set_parent_to_siblings(self, g):
        self.parent_to_siblings = {}

        parents = g.predecessors(self.prefix_uri)
        for parent in parents:
            all_children = g.successors(parent)
            children_minus_this_event = set(all_children) - {self.prefix_uri}
            children_minus_this_event_full = {
                from_short_uri_to_full_uri(child)
                for child in children_minus_this_event
            }
            self.parent_to_siblings[from_short_uri_to_full_uri(parent)] = children_minus_this_event_full

class Incident:
    """
    represents a Wikidata Incident, e.g.,

    title_labels={'en' : '2014 Acre gubernatorial election'}
    title_id='Q51336711'
    full_uri='http://www.wikidata.org/entity/Q51336711'
    prefix_uri='wd:Q51336711'
    properties=[prop_obj], # instances of class Property

    """
    def __init__(self,
                 title_labels,
                 title_id,
                 full_uri,
                 prefix_uri,
                 properties,
                 ):
        self.title_labels = title_labels
        self.label_to_show = self.set_label_to_show()
        self.title_id = title_id
        self.full_uri = full_uri
        self.prefix_uri = prefix_uri
        self.properties = properties
        self.unique_properties = {prop_obj.full_uri for prop_obj in self.properties}


    def __str__(self):
        info = ['Information about Incident:']

        attrs = ['title_labels',
                 'title_id',
                 'full_uri',
                 'prefix_uri']

        for attr in attrs:
            info.append(f'ATTR {attr} has value: {getattr(self, attr)}')

        return '\n'.join(info)

    def set_label_to_show(self):
        label_to_show = self.title_labels.get('en', None)

        if label_to_show is None:
            for lang, label in self.title_labels.items():
                label_to_show = label
                break

        return label_to_show


class Property:
    """
    represents a Wikidata property, e.g.,

    title_labels={'en' : 'country'}
    title_id='P17'
    full_uri='http://www.wikidata.org/entity/P17'
    prefix_uri='wdt:P17'
    """
    def __init__(self,
                 title_labels,
                 title_id,
                 full_uri,
                 prefix_uri
                 ):
        self.title_labels = title_labels
        self.label_to_show = self.set_label_to_show()
        self.title_id = title_id
        self.full_uri = full_uri
        self.prefix_uri = prefix_uri

    def __str__(self):
        info = ['Information about Property:']

        attrs = ['title_labels',
                 'title_id',
                 'full_uri',
                 'prefix_uri']
        for attr in attrs:
            info.append(f'ATTR {attr} has value: {getattr(self, attr)}')

        return '\n'.join(info)

    def set_label_to_show(self):
        label_to_show = self.title_labels.get('en', None)

        if label_to_show is None:
            for lang, label in self.title_labels.items():
                label_to_show = label
                break

        return label_to_show


if __name__ == '__main__':
    prop_obj = Property(title_labels={'en' : 'country'},
                        title_id='P17',
                        full_uri='http://www.wikidata.org/entity/P17',
                        prefix_uri='wdt:P17')
    print()
    print(prop_obj)

    inc_obj = Incident(title_labels={'en' : '2014 Acre gubernatorial election'},
                       title_id='Q51336711',
                       full_uri='http://www.wikidata.org/entity/Q51336711',
                       prefix_uri='wd:Q51336711',
                       properties=[prop_obj])

    print()
    print(inc_obj)

    event_type_obj = EventType(title_labels={'en' : 'election'},
                               title_id='Q40231',
                               full_uri='http://www.wikidata.org/entity/Q40231',
                               prefix_uri='wd:Q40231')

    print(event_type_obj)