import wd_classes

def validate(event_type_coll_obj):

    # properties
    prop_to_label = {
        'http://www.wikidata.org/prop/direct/P17' : 'country',
        'http://www.wikidata.org/prop/direct/P585' : 'point in time'
    }

    for prop_uri, needed_label in prop_to_label.items():
        prop_obj = event_type_coll_obj.prop_id_to_prop_obj[prop_uri]
        prop_obj.label_to_show == needed_label, f'mismatch between expected {needed_label} and actual label {prop_obj.label_to_show}'

    # incidents
    inc_uri_to_keyword = {
        'http://www.wikidata.org/entity/Q699872' : 'election'
    }

    for inc_uri, keyword in inc_uri_to_keyword.items():
        inc_obj = event_type_coll_obj.inc_id_to_inc_obj[inc_uri]
        assert keyword in inc_obj.label_to_show, f'needed keyword {keyword} not found in label {inc_obj.label_to_show}'

    # event type -> incidents
    evt_to_min_num_incidents = {
        'http://www.wikidata.org/entity/Q40231' : 5000,
        'http://www.wikidata.org/entity/Q22938576' : 50
    }
    for evt, min_num_incidents in evt_to_min_num_incidents.items():
        event_obj = event_type_coll_obj.event_type_id_to_event_type_obj[evt]
        num_incidents = len(event_obj.incidents)
        assert num_incidents >=  min_num_incidents, f'lower num incidents than expected minimum of {min_num_incidents} and found {num_incidents}'


wd_cache_folder = 'wd_cache'
pickle_path = f'{wd_cache_folder}/ev_type_coll.p'

event_type_coll_obj = wd_classes.EventTypeCollection(path_subclass_of_rels=f'{wd_cache_folder}/subclass_of.json',
                                                     path_instance_of_rels=f'{wd_cache_folder}/instance_of.json',
                                                     path_inc_to_labels=f'{wd_cache_folder}/inc_to_labels.json',
                                                     path_inc_to_props=f'{wd_cache_folder}/inc_to_props.json',
                                                     path_event_type_to_labels=f'{wd_cache_folder}/event_type_to_labels.json',
                                                     path_prop_to_labels=f'{wd_cache_folder}/prop_to_labels.json',
                                                     root_node='http://www.wikidata.org/entity/Q1656682',
                                                     needed_properties={'http://www.wikidata.org/prop/direct/P17'},
                                                     properties_to_ignore={'http://www.wikidata.org/prop/direct/P31', 'http://www.wikidata.org/prop/direct/P279'},
                                                     min_leaf_incident_freq=3,
                                                     verbose=3)


validate(event_type_coll_obj)

print(event_type_coll_obj)

event_type_coll_obj.pickle_it(pickle_path)








