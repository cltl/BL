bash represent_wd.sh

bash create_input_txt_mwep.sh

python call_mwep.py --path_config_json="../config/v1.json" --verbose="1"

python mwep_integrations.py --path_config_json="../config/v1.json" --verbose="2"

# call Open-Sesame
python run_open_sesame.py --path_config_json="../config/v1.json" --verbose="2"

# integrate structured data
python integrate_structured_data.py --path_config_json="../config/v1.json" --verbose="2"

# add lexicon data
python add_lexicon_data.py --path_config_json="../config/v1.json" --verbose="2"

# add typical frames
python ../res/typical_frames/typical_frames.py --path_config_json="../config/v1.json" --verbose="2"

# add SEM representation
python convert_to_sem.py --path_config_json="../config/v1.json" --verbose="2"

# add JSON version
python write_structured_and_unstructured.py --path_config_json="../config/v1.json" --verbose="2"

# add descriptive statistics
python write_stats.py --path_config_json="../config/v1.json" --verbose="2"

# add README, LICENSE
python add_readme_license.py --path_config_json="../config/v1.json" --verbose="2"


