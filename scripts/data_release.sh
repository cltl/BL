bash represent_wd.sh

bash create_input_txt_mwep.sh

python call_mwep.py --path_config_json="../config/v1.json" --verbose="1"

python mwep_integrations.py --path_config_json="../config/v1.json" --verbose="2"

# TODO: call Open-Sesame

# integrate structured data
python integrate_structured_data.py --path_config_json="../config/v1.json" --verbose="2"

# add lexicon data
python add_lexicon_data.py --path_config_json="../config/v1.json" --verbose="2"

# add SEM representation
python convert_to_sem.py --path_config_json="../config/v1.json" --verbose="2"

# TODO: add JSON version

# TODO: add descriptive statistics

# TODO: add README, LICENSE


