#!/bin/sh

source ../env/bin/activate

IDX=$1
SUBSET=$2

python3 col_comparison_subset.py $IDX $SUBSET
