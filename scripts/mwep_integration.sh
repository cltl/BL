#!/usr/bin/env bash

python mwep_integration.py \
 --path_ev_type_coll="../wd_cache/ev_type_coll.p"\
 --path_mwep_repo="/Users/marten/PycharmProjects/multilingual-wiki-event-pipeline"\
 --path_inc_coll_obj="/Users/marten/PycharmProjects/BLE/development/Q2540467_nl,it,en.bin"\
 --path_mwep_wiki_output="/Users/marten/PycharmProjects/BLE/development/wiki_output"\
 --path_wd_wiki_output="/Users/marten/PycharmProjects/BLE/wiki_output"\
 --verbose=3