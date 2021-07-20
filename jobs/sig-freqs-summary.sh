#!/bin/sh

source ../env/bin/activate

ALPHA=$1
N_HISTOGRAM_BINS=$2
SIG_FREQ_TABLE_PATH=$3

python3 sig_freqs_summary.py $ALPHA $N_HISTOGRAM_BINS $SIG_FREQ_TABLE_PATH
