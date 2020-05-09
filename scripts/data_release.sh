bash represent_wd.sh

bash create_input_txt_mwep.sh

python call_mwep.py --path_config_json="../config/v0.json" --verbose="1"

python mwep_integrations.py --path_config_json="../config/v0.json" --verbose="2"

# TODO: call Open-Sesame

# TODO: integrate structured data
python integrate_structured_data.py --path_config_json="../config/v0.json" --verbose="2"

# add lexicon data
python add_lexicon_data.py --path_config_json="../config/v0.json" --verbose="2"

# TODO: add SEM representation

# TODO: add JSON version

# TODO: add descriptive statistics

# TODO: add README, LICENSE


