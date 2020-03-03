import sys
import pickle

sys.path.append('resources/BL')

ev_type_coll = pickle.load(open('data/ev_type_coll_updated.p',
                                'rb'))

# get all reference texts of event type http://www.wikidata.org/entity/Q4504495
event_types = {
'Q464980',
'Q132241',
'Q4504495',
'Q3001412',
'Q220505',
'Q40244',
'Q645883'}

for event_type in event_types:
    naf_paths = ev_type_coll.get_paths_of_reftexts_of_one_event_subgraph(f'http://www.wikidata.org/entity/{event_type}',
                                                                         'data/wiki_output',
                                                                         verbose=1)
