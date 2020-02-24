"""
Incorporate MWEP (https://github.com/cltl/multilingual-wiki-event-pipeline)
output into EventTypeCollection as defined in wd_classes.py

Usage:
  mwep_integration.py --path_ev_type_coll=<path_ev_type_coll> --path_mwep_repo=<path_mwep_repo>\
  --path_inc_coll_obj=<path_inc_coll_obj>  --path_mwep_wiki_output=<path_mwep_wiki_output>\
  --path_wd_wiki_output=<path_wd_wiki_output> --verbose=<verbose>

Options:
    --path_ev_type_coll=<path_ev_type_coll> path where the pickled EventTypeCollection is stored on disk
    --path_mwep_repo=<path_mwep_repo> path where the MWEP repository is stored on disk
    --path_inc_coll_obj=<path_inc_coll_obj> path where the pickled IncidentCollection from MWEP is stored on disk
    --path_mwep_wiki_output=<path_mwep_wiki_output> path to folder where the NAF files are stored as output of running MWEP
    --path_wd_wiki_output=<path_wd_wiki_output> path to folder where the NAF files belonging to EventTypeCollection are stored
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout
"""
from docopt import docopt
import sys
import pickle
sys.path.append('../')

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
ev_type_coll = pickle.load(open(arguments['--path_ev_type_coll'],
                                'rb'))

ev_type_coll.incorporate_incident_collection(path_to_mwep_repo=arguments['--path_mwep_repo'],
                                             path_to_incident_coll_obj=arguments['--path_inc_coll_obj'],
                                             path_mwep_wiki_output_folder=arguments['--path_mwep_wiki_output'],
                                             path_wd_wiki_output_folder=arguments['--path_wd_wiki_output'],
                                             verbose=verbose)

# overwrite EventTypeCollection on disk
ev_type_coll.pickle_it(arguments['--path_ev_type_coll'])