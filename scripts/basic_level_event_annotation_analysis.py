"""
Analyze Basic Level Event annotations

Input format is

all_annotations_folder
	USERNAME
		other
		sport
		test


Usage:
  basic_level_event_annotation_analysis.py --all_annotations_folder=<all_annotations_folder>\
    --path_to_sample_graph_edges=<path_to_sample_graph_edges>\
    --results_folder=<results_folder>\
    --users=<users> --batches=<batches>
     --verbose=<verbose>

Options:
    --all_annotations_folder=<all_annotations_folder> folder of the format see above
    --path_to_sample_graph_edges=<path_to_sample_graph_edges> path to nx edge list
    --results_folder=<results_folder> the results folder (overwritten if exists)
    --users=<users> the users concatenated by ---, probably "Piek---Antske"
    --batches=<batches> the batches to consider, probably "other---sport"
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python basic_level_event_annotation_analysis.py --all_annotations_folder="../ble_annotation"\
    --path_to_sample_graph_edges="../basic_level_inspection/sample.edges"\
    --results_folder="../ble_annotation/results" \
    --users="Piek---Antske" --batches="other---sport"\
    --verbose=2
"""
from docopt import docopt
import os
import shutil

import annotation_utils as utils

ANNOTATION_TASKS = ["participants", "subevents"]

# load arguments
arguments = docopt(__doc__)
output_folder = arguments['--results_folder']
main_anno_folder = arguments['--all_annotations_folder']
path_edge_list = arguments['--path_to_sample_graph_edges']

users = list(arguments['--users'].split('---'))
batches =list(arguments['--batches'].split('---'))
verbose = int(arguments['--verbose'])

print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.mkdir(output_folder)

if verbose >= 1:
    print()
    print(f'(re)created results folder {output_folder}')

edge_to_user_to_task_to_value = utils.combine_annotations(users=users,
                                                          batches=batches,
                                                          main_anno_folder=main_anno_folder,
                                                          verbose=verbose)


for annotation_task in ANNOTATION_TASKS:
    utils.compute_agreement(edge_to_user_to_task_to_value,
                            annotation_task,
                            output_folder=output_folder,
                            verbose=verbose)


sample_g = utils.load_graph_from_edgelist(path_to_edge_list=path_edge_list,
                                          verbose=verbose)

sample_anno_g = utils.update_sample_graph_with_annotations(sample_graph=sample_g,
                                                           edge_to_user_to_task_to_value=edge_to_user_to_task_to_value,
                                                           verbose=verbose)


annotation_task_to_ble_info = {}
for annotation_task in ANNOTATION_TASKS:

    if verbose >= 2:
        print()
        print(f'analyzing for task {annotation_task}')
        task_ble_info = utils.determine_candidate_basic_levels(g=sample_anno_g,
                                                               annotation_task=annotation_task,
                                                               users=users,
                                                               verbose=verbose)

        annotation_task_to_ble_info[annotation_task] = task_ble_info


for annotation_task in ANNOTATION_TASKS:
    utils.ble_analysis(candidate_ble_info=annotation_task_to_ble_info,
                       output_folder=output_folder,
                       verbose=verbose)


