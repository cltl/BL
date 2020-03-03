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
    --results_folder=<results_folder>\
    --users=<users> --batches=<batches>
     --verbose=<verbose>

Options:
    --all_annotations_folder=<all_annotations_folder> folder of the format see above
    --results_folder=<results_folder> the results folder (overwritten if exists)
    --users=<users> the users concatenated by ---, probably "Piek---Antske"
    --batches=<batches> the batches to consider, probably "other---sport"
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python basic_level_event_annotation_analysis.py --all_annotations_folder="../development/annotations"\
    --results_folder="../development/results" \
    --users="Piek---Antske" --batches="test"\
    --verbose=2
"""
from docopt import docopt
import os
import shutil
from collections import defaultdict

import annotation_utils

ANNOTATION_TASKS = ["participants", "subevents"]

# load arguments
arguments = docopt(__doc__)
output_folder = arguments['--results_folder']
main_anno_folder = arguments['--all_annotations_folder']

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

edge_to_user_to_task_to_value = annotation_utils.combine_annotations(users=users,
                                                                     batches=batches,
                                                                     main_anno_folder=main_anno_folder,
                                                                     verbose=verbose)


for annotation_task in ANNOTATION_TASKS:
    annotation_utils.compute_agreement(edge_to_user_to_task_to_value,
                                       annotation_task,
                                       output_folder=output_folder,
                                       verbose=verbose)