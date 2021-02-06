#!/bin/sh

source ../env/bin/activate

FEAT_MAP=$1

python3 create_subset.py data/data.csv $FEAT_MAP adni
