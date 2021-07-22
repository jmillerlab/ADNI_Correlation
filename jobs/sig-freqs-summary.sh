#!/bin/sh

source ../env/bin/activate

ANALYSIS_NAME=$1
N_HISTOGRAM_BINS=$2
SIG_FREQ_TABLE_PATH=$3

python3 sig_freqs_summary.py $ANALYSIS_NAME $N_HISTOGRAM_BINS $SIG_FREQ_TABLE_PATH
