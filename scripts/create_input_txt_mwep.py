"""
Create a txt file with all event types to be run with MWEP

Usage:
  create_input_txt_mwep.py --path_ev_coll_obj=<path_ev_coll_obj> --output_path=<output_path> --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_ev_coll_obj=<path_ev_coll_obj> path to pickled EventTypeCollection class
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --output_path=<output_path> path where txt is stored with all the event types to be run with MWEP
    OUTPUT_FOLDER/event_types.txt is stored
    --verbose=<verbose> verbose level

Example:
    python create_input_txt_mwep.py\
     --path_ev_coll_obj="../wd_cache/ev_type_coll.p"\
     --path_config_json="../config/v0.json"\
     --output_path="../wd_cache/event_types.txt"\
     --verbose=2
"""
from docopt import docopt
import sys
import json
sys.path.append('../')
import pickle

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
settings = json.load(open(arguments['--path_config_json']))

ev_coll_obj = pickle.load(open(arguments['--path_ev_coll_obj'], 'rb'))

ev_coll_obj.get_subsumers_of_set_of_event_types(event_types=settings['event_types'],
                                                output_path=arguments['--output_path'],
                                                verbose=verbose)