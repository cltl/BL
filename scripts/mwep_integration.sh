#!/usr/bin/env bash

base="../wd_cache/ev_type_coll.p"
updated="../wd_cache/ev_type_coll_updated.p"
rm $updated
cp $base $updated

# folder where bin files are stored (output from MWEP)
bin_folder="/Users/marten/PycharmProjects/BLE/development/"

for EVTYPE in Q2540467
do
    python mwep_integration.py \
     --path_ev_type_coll=$updated\
     --outpath_ev_type_coll=$updated\
     --path_mwep_repo="/Users/marten/PycharmProjects/multilingual-wiki-event-pipeline"\
     --path_inc_coll_obj="${bin_folder}${EVTYPE}_nl,it,en.bin"\
     --path_mwep_wiki_output="/Users/marten/PycharmProjects/BLE/development/wiki_output"\
     --path_wd_wiki_output="/Users/marten/PycharmProjects/BLE/wiki_output"\
     --verbose=3
done