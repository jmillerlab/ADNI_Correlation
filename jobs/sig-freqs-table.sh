#!/bin/sh

source ../env/bin/activate

DICT_PATH=$1
TABLE_PATH=$2

python3 sig_freqs_table.py ${DICT_PATH} ${TABLE_PATH}
