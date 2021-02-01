#!/bin/sh

source ../env/bin/activate

COMP_TYPE=$1

python3 counts_table.py $COMP_TYPE
