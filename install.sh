#!/usr/bin/env bash



rm -rf res
mkdir res

cd res

git clone https://github.com/cltl/typical_frames
cd typical_frames
pip install -r requirements.txt
cd ..

git clone https://github.com/cltl/Dutch_FrameNet_Lexicon
cd Dutch_FrameNet_Lexicon
pip install -r requirements.txt
bash install.sh
cd bash_scripts
bash represent_using_FrameNet_class.sh
bash lexicon_data_for_tool.sh

