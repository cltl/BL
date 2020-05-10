"""
Convet to SEM

python convert_to_sem.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  convert_to_sem.py --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python convert_to_sem.py --path_config_json="../config/v0.json" --verbose="2"
"""
from docopt import docopt
import json
import pickle
import os

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

ttl_path = os.path.join(settings['paths']['data_release_json_folder'],
                        f'{settings["project"]}.ttl')
ev_coll_obj.serialize(event_types=settings['event_types'],
                      filename=ttl_path)
