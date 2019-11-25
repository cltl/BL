#!/usr/bin/env bash



rm -rf resources
mkdir resources

cd resources
git clone https://github.com/cltl/multilingual-wiki-event-pipeline
cd multilingual-wiki-event-pipeline
python -c "import utils;utils.load_ontology_as_directed_graph('ontology', 'wd:Q1656682', verbose=2)"