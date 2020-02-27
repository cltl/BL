import sys
import pickle
sys.path.append('../')

ev_type_coll = pickle.load(open('../wd_cache/ev_type_coll_updated.p',
                                'rb'))

naf_paths = ev_type_coll.get_paths_of_reftexts_of_one_event_subgraph('http://www.wikidata.org/entity/Q2540467',
                                                                     '/Users/marten/PycharmProjects/BLE/wiki_output',
                                                                     verbose=1)
