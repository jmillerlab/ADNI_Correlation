#!/bin/sh

source ../env/bin/activate

ALPHA=$1

python3 significance_frequencies.py ${ALPHA}
