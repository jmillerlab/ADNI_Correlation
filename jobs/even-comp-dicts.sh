#!/bin/sh

source ../env/bin/activate

COMP_DICT_DIR=$1
N_COMPS_PER_FILE=$2

python3 even_comp_dicts.py ${COMP_DICT_DIR} ${N_COMPS_PER_FILE}
