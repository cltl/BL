#!/usr/bin/env bash


cd ..
rm -rf output
mkdir output

rm -rf log
mkdir log

python run_ble.py --threshold=0 > log/0.out 2> log/0.err &
python run_ble.py --threshold=10 > log/10.out 2> log/10.err &
python run_ble.py --threshold=20 > log/20.out 2> log/20.err &
python run_ble.py --threshold=30 > log/30.out 2> log/30.err &
python run_ble.py --threshold=40 > log/40.out 2> log/40.err &
python run_ble.py --threshold=50 > log/50.out 2> log/50.err &