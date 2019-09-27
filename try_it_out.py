import ble_classes
import networkx as nx


# path to directed graph (see bottom of ble_classes.py for example)
path = '../multilingual-wiki-event-pipeline/ontology/g.p'
g = nx.read_gpickle(path)

ble_coll_obj = ble_classes.BLECollection(g=g,
                                         resource='Wikidata',
                                         output_folder='output',
                                         root_node='wd:Q1656682',
                                         weight_property='occurrence_frequency',
                                         subsumer_threshold=0,
                                         root_zero=True,
                                         verbose=1)


print(ble_coll_obj)
ble_coll_obj.print_bles(min_cumulative_freq=500)

