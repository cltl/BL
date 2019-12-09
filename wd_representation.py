import wd_classes



wd_cache_folder = 'wd_cache'

event_type_coll_obj = wd_classes.EventTypeCollection(path_subclass_of_rels=f'{wd_cache_folder}/subclass_of.json',
                                                     path_instance_of_rels=f'{wd_cache_folder}/instance_of.json',
                                                     path_inc_to_labels=f'{wd_cache_folder}/inc_to_labels.json',
                                                     path_inc_to_props=f'{wd_cache_folder}/inc_to_props.json',
                                                     path_event_type_to_labels=f'{wd_cache_folder}/event_type_to_labels.json',
                                                     path_prop_to_labels=f'{wd_cache_folder}/prop_to_labels.json',
                                                     root_node='http://www.wikidata.org/entity/Q1656682',
                                                     needed_properties={'http://www.wikidata.org/prop/direct/P17'},
                                                     min_leaf_incident_freq=0,
                                                     verbose=3)





