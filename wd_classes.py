import json
from _collections import defaultdict



# TODO: finalize update_event_types_with_incidents
# TODO: represent as directed graph
# TODO: all remaining methods

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
                 min_leaf_incident_freq=0,
                 verbose=0):
        self.verbose = verbose

        self.prop_id_to_prop_obj = self.get_property_to_property_obj(path_prop_to_labels=path_prop_to_labels)
        self.inc_id_to_inc_obj = self.get_inc_to_inc_obj(path_inc_to_labels=path_inc_to_labels,
                                                         path_inc_to_props=path_inc_to_props,
                                                         needed_properties=needed_properties)
        self.event_type_id_to_event_type_obj = self.get_event_type_to_eventtype_obj(path_event_type_to_labels=path_event_type_to_labels)
        self.update_event_types_with_incidents(path_instance_of_rels=path_instance_of_rels)



    def get_property_to_property_obj(self, path_prop_to_labels):
        """
        load mapping from property id (full uri) -> instance of class Property
        """
        with open(path_prop_to_labels) as infile:
            prop_to_label_rels = json.load(open(path_prop_to_labels))

        prop_to_labels = defaultdict(set)
        for prop_uri, label in prop_to_label_rels:
            prop_to_labels[prop_uri].add(label)

        prop_id_to_prop_obj = dict()
        for prop_uri, labels in prop_to_labels.items():

            label = list(labels)[0]
            title_id = prop_uri.split('/')[-1]

            prop_obj = Property(title_label=label,
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

            inc_to_labels = defaultdict(set)
            for inc_uri, label in inc_to_label_rels:
                inc_to_labels[inc_uri].add(label)

        with open(path_inc_to_props) as infile:
            inc_to_prop_rels = json.load(infile)

            inc_to_props = defaultdict(set)
            for inc_uri, prop_uri in inc_to_prop_rels:
                inc_to_props[inc_uri].add(prop_uri)


        inc_uri_to_inc_obj = dict()

        for inc_uri, labels in inc_to_labels.items():

            props = inc_to_props[inc_uri]
            title_id = inc_uri.split('/')[-1]

            # check if all mandatory properties are present
            skip = False
            for needed_prop in needed_properties:
                if needed_prop not in props:
                    skip = True

            if skip:
                continue

            label = list(labels)[0]

            prop_objs = []
            for prop in props:
                if prop in self.prop_id_to_prop_obj:
                    prop_objs.append(self.prop_id_to_prop_obj[prop])

            inc_obj = Incident(title_label=label,
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

            event_type_obj = EventType(title_label=label,
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
                if self.verbose >= 3:
                    print()
                    print(event_type_uri)
                    input('continue?')
                continue

            incident_uris = event_type_uri_to_incident_uri[event_type_uri]

            event_type_obj.incidents = incident_uris

            num_inc_uris_added.append(len(incident_uris))

        if self.verbose >= 1:
            print()
            print(f'updated incidents attributes for {len(num_inc_uris_added)} event types')

    def represent_as_directed_graph(self): pass

    def compute_stats(self): pass


class EventType(EventTypeCollection):
    """
    represents a Wikidata event type, e.g.,

    title_label='election',
    title_id='Q40231',
    full_uri='http://www.wikidata.org/entity/Q40231',
    prefix_uri='wd:Q40231',
    """
    def __init__(self,
                 title_label,
                 title_id,
                 full_uri,
                 prefix_uri,
                 ):
        self.title_label = title_label
        self.title_id = title_id
        self.full_uri = full_uri
        self.prefix_uri = prefix_uri
        self.incidents = []

    def __str__(self):
        info = ['Information about EventType:']

        attrs = ['title_label',
                 'title_id',
                 'full_uri',
                 'prefix_uri']
        for attr in attrs:
            info.append(f'ATTR {attr} has value: {getattr(self, attr)}')

        info.append(f'ATTR instances has {len(self.incidents)} items')

        return '\n'.join(info)


    def aggregrate_properties(self): pass

    def set_cue_validities(self): pass

    def set_incident_freq(self): pass


class Incident:
    """
    represents a Wikidata Incident, e.g.,

    title_label='2014 Acre gubernatorial election',
    title_id='Q51336711',
    full_uri='http://www.wikidata.org/entity/Q51336711',
    prefix_uri='wd:Q51336711',
    properties=[prop_obj], # instances of class Property

    """
    def __init__(self,
                 title_label,
                 title_id,
                 full_uri,
                 prefix_uri,
                 properties,
                 ):
        self.title_label = title_label
        self.title_id = title_id
        self.full_uri = full_uri
        self.prefix_uri = prefix_uri
        self.properties = properties

    def __str__(self):
        info = ['Information about Incident:']

        attrs = ['title_label',
                 'title_id',
                 'full_uri',
                 'prefix_uri']

        for attr in attrs:
            info.append(f'ATTR {attr} has value: {getattr(self, attr)}')

        props = ' '.join([prop_obj.title_label for prop_obj in self.properties])
        info.append(f'ATTR properties has value: {props}')

        return '\n'.join(info)


class Property:
    """
    represents a Wikidata property, e.g.,

    title_label='country',
    title_id='P17',
    full_uri='http://www.wikidata.org/entity/P17',
    prefix_uri='wdt:P17'
    """
    def __init__(self,
                 title_label,
                 title_id,
                 full_uri,
                 prefix_uri
                 ):
        self.title_label = title_label
        self.title_id = title_id
        self.full_uri = full_uri
        self.prefix_uri = prefix_uri

    def __str__(self):
        info = ['Information about Property:']

        attrs = ['title_label',
                 'title_id',
                 'full_uri',
                 'prefix_uri']
        for attr in attrs:
            info.append(f'ATTR {attr} has value: {getattr(self, attr)}')

        return '\n'.join(info)


if __name__ == '__main__':
    prop_obj = Property(title_label='country',
                        title_id='P17',
                        full_uri='http://www.wikidata.org/entity/P17',
                        prefix_uri='wdt:P17')
    print()
    print(prop_obj)

    inc_obj = Incident(title_label='2014 Acre gubernatorial election',
                       title_id='Q51336711',
                       full_uri='http://www.wikidata.org/entity/Q51336711',
                       prefix_uri='wd:Q51336711',
                       properties=[prop_obj])

    print()
    print(inc_obj)

    event_type_obj = EventType(title_label='election',
                               title_id='Q40231',
                               full_uri='http://www.wikidata.org/entity/Q40231',
                               prefix_uri='wd:Q40231',
                               incidents=[inc_obj])

    print(event_type_obj)