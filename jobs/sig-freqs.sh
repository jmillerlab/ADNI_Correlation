#!/bin/sh

source ../env/bin/activate

COMP_DICT_DIR=$1
FILE_PATH=$2

python3 sig_freqs.py ${COMP_DICT_DIR} ${FILE_PATH}
