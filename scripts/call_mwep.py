"""
Call MWEP

python call_mwep.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  call_mwep.py --path_config_json=<path_config_json>\
   --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python call_mwep.py --path_config_json="../config/v0.json" --verbose="2"
"""
from docopt import docopt
import json
import os
import shutil
import subprocess

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
settings = json.load(open(arguments['--path_config_json']))

mwep_folder=settings['paths']['mwep_folder']
mwep_settings_path = os.path.join(mwep_folder,
                                  'config',
                                  'mwep_settings.json')
if os.path.exists(mwep_settings_path):
    os.remove(mwep_settings_path)
shutil.copy(settings['paths']['mwep_settings'], mwep_settings_path)

event_types_txt = os.path.join(mwep_folder,
                               'config',
                               'event_types.txt')
if os.path.exists(event_types_txt):
    os.remove(event_types_txt)
shutil.copy(settings['paths']['event_types_txt'], event_types_txt)

project = settings['mwep']['project']
languages = '-'.join(settings['mwep']['languages'])
wikipedia_sources = settings['mwep']['wikipedia_sources']

subcommands = [
    f'cd {mwep_folder}',
    '&&',
    'python main.py',
    f'--config_path="config/mwep_settings.json"',
    f'--project="{project}"',
    f'--path_event_types="config/event_types.txt"',
    f'--languages="{languages}"',
    f'--wikipedia_sources={wikipedia_sources}',
    '--verbose=1'
]
command = ' '.join(subcommands)
print(command)
result = subprocess.check_output(command, shell=True)
print(result)
