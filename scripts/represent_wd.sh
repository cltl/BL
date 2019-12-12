#!/usr/bin/env bash
cd ..

rm -rf log
mkdir log

python wd_utils.py > log/queries.out 2> log/queries.err
python wd_representation.py > log/wd_representation.out 2> log/wd_representation.err

