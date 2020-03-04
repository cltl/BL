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
path = 'wd_cache/g.p'
g = nx.read_gpickle(path)

bl_coll_obj = bl_classes.BLCollection(g=g,
                                      resource='Wikidata',
                                      output_folder='output',
                                      root_node='Q1656682',
                                      weight_property='occurrence_frequency',
                                      subsumer_threshold=threshold,
                                      root_zero=True,
                                      verbose=1)

utils.get_overview_table(input_folder='output',
                         excel_path='output/overview.xlsx',
                         latex_path='output/overview.tex')

df = bl_coll_obj.print_bles(min_cumulative_freq=500,
                            max_cumulative_freq=10000,
                            verbose=1)

df.to_excel(f'output/{threshold}.xlsx')

bl_txt_path = f'output/{threshold}.txt'
bl_ids = list(df['Node ID'])
with open(bl_txt_path, 'w') as outfile:
    outfile.write(' '.join(bl_ids))

