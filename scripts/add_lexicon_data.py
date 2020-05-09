"""
Add FrameNet lexicon data to a data release folder

python add_lexicon_data.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  add_lexicon_data.py --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python add_lexicon_data.py --path_config_json="../config/v0.json" --verbose="2"
"""
from docopt import docopt
import json
import os 
import shutil

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
settings = json.load(open(arguments['--path_config_json']))

shutil.copytree(settings['paths']['lexicon_data'],
                settings['paths']['data_release_frames_folder'])
