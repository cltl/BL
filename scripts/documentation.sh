#!/usr/bin/env bash


cd ..
pyreverse wd_classes.py
dot -Tpdf classes.dot -o documentation/wd_classes.pdf
rm classes.dot

