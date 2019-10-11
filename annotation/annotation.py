import networkx as nx
from graphviz import Source
import json
import shutil
import os
import pickle
import pandas
import random
import utils

def clean_label(label, forbidden={'/', '&'}):

    table = {ord(char) : ' '
             for char in forbidden}

    label = label.translate(table)
    return label


def get_sample(iterable, number_of_items):

    if len(iterable) < number_of_items:
        number_of_items = len(iterable)

    the_sample = random.sample(iterable, number_of_items)

    return the_sample

def create_node_string(identifier, 
                       event_type,
                       event_type_uri,
                       example_incidents):
    """
    """    
    line_one = f'{identifier}[label=<<table>'
    line_two = f'<tr><td href="{event_type_uri}">{event_type}</td></tr>'
    
    lines = [line_one, line_two]
    
    for index, uri in enumerate(example_incidents, 1):
        line = f'<tr><td href="{uri}">Example {index}</td></tr>'
        lines.append(line)
    
    last_line = '</table>>]'
    lines.append(last_line)
    
    return '\n'.join(lines)

example_incidents = [
    'https://www.wikidata.org/wiki/Q127905',
    'https://www.wikidata.org/wiki/Q127906',
    'https://www.wikidata.org/wiki/Q1804155'
]
a_node_string = create_node_string(identifier='A',
                   event_type='election',
                   event_type_uri='https://www.wikidata.org/wiki/Q40231',
                   example_incidents=example_incidents)


# load input
graph_path = '../../multilingual-wiki-event-pipeline/ontology/g.p'
g = nx.read_gpickle(graph_path)
node2occurrences_path = '../../multilingual-wiki-event-pipeline/ontology/eventtype2incidents.p'
node2occurrences = pickle.load(open(node2occurrences_path, 'rb'))
annotators = ['Andras', 'Klaudia', 'Simos', 'Lauren', 'Sophie', 'Jonathan', 'Lisa']

if os.path.exists('output'):
    shutil.rmtree('output')
os.mkdir('output')

output_folder = f'output'
svg_folder = f'output/svg'
annotations_folder = f'output/annotations'

# recreate directories
if os.path.isdir(output_folder):
    shutil.rmtree(output_folder)
os.mkdir(output_folder)
os.mkdir(svg_folder)
os.mkdir(annotations_folder)

id2tree_path = f'input/to_annotate.json'
id_2nodes_and_edges = json.load(open(id2tree_path))
id_2parents = dict()

# create dot and svg files
num_parents = []

for id_, nodes_edges in id_2nodes_and_edges.items():
    gv_path = f'{svg_folder}/{id_}.gv'

    id_2parents[id_] = nodes_edges['parents']

    num_parents.append(len(nodes_edges['parents']))
    with open(gv_path, 'w') as outfile:
        outfile.write('digraph G {\n\n')

        for eventtype_wdtid in nodes_edges['nodes']:
            uri = f'https://www.wikidata.org/wiki/{eventtype_wdtid[3:]}'

            info = g.nodes[eventtype_wdtid]

            incidents = node2occurrences[eventtype_wdtid]
            example_incidents = get_sample(incidents, 3)

            label = info['label']
            label = clean_label(label)

            a_node_string = create_node_string(
                       identifier=eventtype_wdtid[3:],
                       event_type=label,
                       event_type_uri=uri,
                       example_incidents=example_incidents)

            outfile.write(a_node_string)

        edges = nodes_edges['edges']
        for source, target in edges:
            outfile.write(f'{source[3:]} -> {target[3:]}\n')
        outfile.write('\n}')

    src = Source(open(gv_path).read())

    try:
        src.render(filename=gv_path, format='svg')
    except Exception as e:
        print(id_, e)


# create files for annotators

id_2answer = {
    'wd:Q17317604' : 'no',
    'wd:Q3001412' : 'yes'
}

prefix = 'http://kyoto.let.vu.nl/~postma/ble/svg/'

items = list(id_2nodes_and_edges)
annotators = ['Andras', 'Klaudia', 'Simos', 'Lauren', 'Sophie', 'Jonathan', 'Lisa']

annotator_to_items = utils.divide_work(items,
                                       annotators,
                                       num_annotations_per_item=3,
                                       ignore=set(id_2answer),
                                       verbose=1)

for annotator, their_items in annotator_to_items.items():
    output_path = f'{annotations_folder}/{annotator}.xlsx'
    list_of_lists = []
    headers = ['ID', 'Comment', 'Parent', 'Answer', 'Parent', 'Answer', 'Parent', 'Answer']

    for id_, nodes_edges in id_2nodes_and_edges.items():

        url = f'{prefix}{id_}.gv.svg'

        if id_ in id_2answer:
            one_row = [url, '', '', id_2answer[id_], '', '', '', '']
        elif id_ in their_items:
            one_row = [url, '', '', '', '', '', '', '']
        else:
            continue

        parents = id_2parents[id_]

        index = 1
        for parent in parents:
            one_row[index] = g.nodes[parent]['label']
            index += 2

        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    df.to_excel(output_path, index=False)
