import bl_classes
import utils
import networkx as nx


# path to directed graph (see bottom of ble_classes.py for example)
path = '../multilingual-wiki-event-pipeline/ontology/g.p'
g = nx.read_gpickle(path)

bl_coll_obj = bl_classes.BLCollection(g=g,
                                        resource='Wikidata',
                                        output_folder='output',
                                        root_node='wd:Q1656682',
                                        weight_property='occurrence_frequency',
                                        subsumer_threshold=0,
                                        root_zero=True,
                                        verbose=1)


utils.get_overview_table(input_folder='output', excel_path='output/overview.xlsx')


