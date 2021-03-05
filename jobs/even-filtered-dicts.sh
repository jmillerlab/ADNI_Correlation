#!/bin/sh

source ../env/bin/activate

ALPHA=$1

python3 even_filtered_dicts.py ${ALPHA}
