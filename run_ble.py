"""
Usage:
  run_ble.py --threshold=<threshold>

Options:
  --threshold=<threshold> the subsumer threshold

Example:
    python run_ble.py --threshold=0
"""
from docopt import docopt
import bl_classes
import utils
import networkx as nx

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

threshold = int(arguments['--threshold'])

# path to directed graph (see bottom of ble_classes.py for example)
path = 'resources/multilingual-wiki-event-pipeline/ontology/g.p'
g = nx.read_gpickle(path)

bl_coll_obj = bl_classes.BLCollection(g=g,
                                      resource='Wikidata',
                                      output_folder='output',
                                      root_node='wd:Q1656682',
                                      weight_property='occurrence_frequency',
                                      subsumer_threshold=threshold,
                                      root_zero=True,
                                      verbose=1)

utils.get_overview_table(input_folder='output',
                         excel_path='output/overview.xlsx')