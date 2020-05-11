#!/usr/bin/env bash

python create_input_txt_mwep.py\
     --path_ev_coll_obj="../wd_cache/ev_type_coll.p"\
     --path_config_json="../config/v1.json"\
     --output_path="../wd_cache/event_types.txt"\
     --verbose=2
