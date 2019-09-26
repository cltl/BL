from graphviz import Source
import json
import shutil
import os
import pandas


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


output_folder = 'output'
svg_folder = 'output/svg'
annotations_folder = 'output/annotations'

# recreate directories
if os.path.isdir(output_folder):
    shutil.rmtree(output_folder)
os.mkdir(output_folder)
os.mkdir(svg_folder)
os.mkdir(annotations_folder)

# load input
json_path = 'input/event_type2info.json'
id2tree_path = 'input/trees.json'
annotators = ['John', 'Peter']
event_type2info = json.load(open(json_path))
id_2tree = json.load(open(id2tree_path))

# create dot and svg files
for id_, tree in id_2tree.items():
    gv_path = f'{svg_folder}/{id_}.gv'
    with open(gv_path, 'w') as outfile:
        outfile.write('digraph G {\n\n')

        for event_type in tree:
            info = event_type2info[event_type]
            a_node_string = create_node_string(
                       identifier=info['identifier'],
                       event_type=event_type,
                       event_type_uri=info['event_uri'],
                       example_incidents=info['example_incidents'])

            outfile.write(a_node_string)

        for source, target in zip(tree, tree[1:]):
            source_id = event_type2info[source]['identifier']
            target_id = event_type2info[target]['identifier']
            outfile.write(f'{source_id} -> {target_id}\n')
        outfile.write('\n}')
    
    src = Source(open(gv_path).read())
    src.render(filename=gv_path, format='svg')

# create files for annotators
for annotator in annotators:
    output_path = f'{annotations_folder}/{annotator}.xlsx'
    list_of_lists = []
    headers = ['ID', 'Answer', 'Options']
    
    for id_, info in id_2tree.items():
        one_row = [id_, '', '--'.join(info)]
        list_of_lists.append(one_row)
    
    df = pandas.DataFrame(list_of_lists, columns=headers)
    
    df.to_excel(output_path, index=False)  
