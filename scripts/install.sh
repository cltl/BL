#!/usr/bin/env bash


rm -rf resources
mkdir resources
cd resources
git clone https://github.com/cltl/bl
cd ..

rm -rf data
mkdir data
cd data
wget http://kyoto.let.vu.nl/~postma/dfn/data_releases/v0.1/ev_type_coll_updated.p
wget http://kyoto.let.vu.nl/~postma/dfn/data_releases/v0.1/wiki_output.zip
unzip wiki_output.zip