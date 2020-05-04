#!/usr/bin/env bash

base="../wd_cache/ev_type_coll.p"
updated="../wd_cache/ev_type_coll_updated.p"
rm -f $updated
cp $base $updated

# folder where bin files are stored (output from MWEP)
bin_folder="/home/postma/multilingual-wiki-event-pipeline/bin"
mwep_folder="/home/postma/multilingual-wiki-event-pipeline"
mwep_wiki_output="/home/postma/multilingual-wiki-event-pipeline/wiki_output"
wd_wiki_output="../wiki_output"

for EVTYPE in Q13219666 Q1079023 Q2912397 Q132241 Q15966540 Q1318941 Q2618461 Q645883 Q858439 Q24050099 Q18131152 Q2627975 Q1478437 Q15061650 Q126701 Q21156425 Q1445650 Q11483816 Q40244 Q56321344 Q22231110 Q22231111 Q93288 Q167170 Q20107484
do
    python mwep_integration.py \
     --path_ev_type_coll=$updated\
     --outpath_ev_type_coll=$updated\
     --path_mwep_repo=$mwep_folder\
     --path_inc_coll_obj="${bin_folder}/${EVTYPE}_en.bin"\
     --path_mwep_wiki_output=$mwep_wiki_output\
     --path_wd_wiki_output=$wd_wiki_output\
     --verbose=3
done
