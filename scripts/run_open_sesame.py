"""
Run open-sesame on English NAF files

python run_open_sesame.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  run_open_sesame.py --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v1.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python run_open_sesame.py --path_config_json="../config/v1.json" --verbose="2"
"""
from docopt import docopt
import json
import sys
import os
import subprocess

sys.path.append('../')

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
settings = json.load(open(arguments['--path_config_json']))

frame_to_info = os.path.join(settings['paths']['lexicon_data'],
                             'frame_to_info.json')

parts = [
    f'cd {settings["open-sesame"]["path_repo"]}',
    '&&',
    "bash run_open_sesame.sh",
    os.path.join(settings['paths']['mwep_wiki_output'], 'en'),
    settings['open-sesame']['tasks'],
    frame_to_info
]
command = ' '.join(parts)
print(command)
result = subprocess.check_output(command, shell=True)
print(result)

naf_out = os.path.join(settings['open-sesame']['path_repo'], 'output', 'NAF')
wd_en_out = os.path.join(settings['paths']['data_release_naf_folder'], 'en')
cp_parts = [
    'find',
    naf_out,
    '-name',
    "'*naf'",
    "-exec",
    "cp",
    "{}",
    wd_en_out,
    "\\;"
    ]
cp_command = ' '.join(cp_parts)
print(cp_command)
result = subprocess.check_output(cp_command, shell=True)
print(result)
