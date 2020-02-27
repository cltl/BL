import sys
import pickle

sys.path.append('resources/BL')

ev_type_coll = pickle.load(open('data/ev_type_coll_updated.p',
                                'rb'))

# get all reference texts of event type http://www.wikidata.org/entity/Q4504495
naf_paths = ev_type_coll.get_paths_of_reftexts_of_one_event_subgraph('http://www.wikidata.org/entity/Q4504495',
                                                                     'data/wiki_output',
                                                                     verbose=1)