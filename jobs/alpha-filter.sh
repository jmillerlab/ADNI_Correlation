#!/bin/sh

source ../env/bin/activate

COMP_DICT_DIR=$1
ALPHA=$2
IDX=$3
SECTION_SIZE=$4
ALPHA_FILTERED_DIR=$5

python3 alpha_filter.py $COMP_DICT_DIR $ALPHA $IDX $SECTION_SIZE $ALPHA_FILTERED_DIR
