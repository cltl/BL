"""
Write structured and unstructured to one JSON file

python write_structured_and_unstructured.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  write_structured_and_unstructured.py --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v1.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python write_structured_and_unstructured.py --path_config_json="../config/v1.json" --verbose="2"
"""
from docopt import docopt
import json
import os
import pickle
import sys

sys.path.append('../')

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
settings = json.load(open(arguments['--path_config_json']))

ev_coll_obj = pickle.load(open(settings['paths']['wd_representation_with_mwep'],
                               'rb'))

if os.path.exists(settings['paths']['typical_frames_path']):
    typical_frames = json.load(open(settings['paths']['typical_frames_path']))
else:
    typical_frames = {}

ev_coll_obj.write_all_to_one_json(event_types=settings['event_types'],
                                  json_folder=settings['paths']['data_release_json_folder'],
                                  unstructured_folder=settings['paths']['data_release_naf_folder'],
                                  typical_frames=typical_frames)

