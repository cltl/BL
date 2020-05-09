"""
Integrate MWEP structured data into Wikidata representation

python integrate_structured_data.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  integrate_structured_data.py --path_config_json=<path_config_json>\
   --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python integrate_structured_data.py --path_config_json="../config/v0.json" --verbose="2"
"""
from docopt import docopt
import json
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

ev_coll_obj.create_json_files(main_event_types=settings['event_types'],
                              json_dir=settings['paths']['data_release_json_folder'],
                              project=settings['mwep']['project'],
                              wd_prefix='http://www.wikidata.org/entity/',
                              verbose=0)
