#!/bin/sh

source ../env/bin/activate

IDX=$1
SUBSET=$2
COMP_DICT_DIR=$3

python3 col_comparison_subset.py $IDX $SUBSET $COMP_DICT_DIR
