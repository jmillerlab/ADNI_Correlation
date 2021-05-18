#!/bin/sh

source ../env/bin/activate

HEADER=$1
ALPHA=$2
MODE=$3

python3 get_correlated_features.py ${HEADER} ${ALPHA} ${MODE}
