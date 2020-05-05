"""
Integrate MWEP output into Wikidata representation

python mwep_integrations.py --path_config_json=<path_config_json> --verbose=<verbose>

Usage:
  mwep_integrations.py --path_config_json=<path_config_json> --verbose=<verbose>

Options:
    --path_config_json=<path_config_json> e.g., ../config/v0.json
    --verbose=<verbose> 0 nothing, 1 descriptive stats, 2 debugging information

Example:
    python mwep_integrations.py --path_config_json="../config/v0.json" --verbose="2"
"""
from docopt import docopt
import json
import os
import subprocess
import shutil

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
settings = json.load(open(arguments['--path_config_json']))

base=settings['paths']['wd_representation_base']
updated=settings['paths']['wd_representation_with_mwep']
if os.path.exists(updated):
    os.remove(updated)
shutil.copy(base, updated)

# folder where bin files are stored (output from MWEP)
bin_folder=settings['paths']['bin_folder']
mwep_folder=settings['paths']['mwep_folder']
mwep_wiki_output=settings['paths']['mwep_wiki_output']
wd_wiki_output=settings['paths']['wd_wiki_output']
path_event_types_txt=settings['paths']['event_types_txt']

languages = ",".join(sorted(settings['mwep']['languages']))

with open(path_event_types_txt) as infile:
    for line in infile:
        evtype = line.strip()
        subcommands = [
            'python mwep_integration.py',
            f'--path_ev_type_coll="{updated}"',
            f'--outpath_ev_type_coll="{updated}"',
            f'--path_mwep_repo="{mwep_folder}"',
            f'--path_inc_coll_obj="{bin_folder}/{evtype}_{languages}.bin"',
            f'--path_mwep_wiki_output="{mwep_wiki_output}"',
            f'--path_wd_wiki_output="{wd_wiki_output}"',
            '--verbose=3'
        ]
        command = ' '.join(subcommands)
        print()
        print(command)
        result = subprocess.check_output(command, shell=True)
        print(result)
