"""
Write descriptive statistics about the data release to disk

python write_stats.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  write_stats.py --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python write_stats.py --path_config_json="../config/v0.json" --verbose="2"
"""
from docopt import docopt
import json
import pickle

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

ev_coll_obj.write_stats(event_types=settings['event_types'],
                        stats_folder=settings['paths']['data_release_stats_folder'],
                        unstructured_folder=settings['paths']['data_release_naf_folder'],
                        languages=settings['mwep']['languages'])
