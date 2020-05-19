"""
Add FrameNet lexicon data to a data release folder

python add_readme_license.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  add_readme_license.py --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python add_readme_license.py --path_config_json="../config/v1.json" --verbose="2"
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

out_dir = settings['paths']['data_release_folder']

for license, path in settings['licenses'].items():
    shutil.copy(src=path,
                dst=out_dir)




