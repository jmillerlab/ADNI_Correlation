#!/bin/sh

source ../env/bin/activate

ALPHA=$1
N_HISTOGRAM_BINS=$2

python3 significance_summary.py $ALPHA $N_HISTOGRAM_BINS
