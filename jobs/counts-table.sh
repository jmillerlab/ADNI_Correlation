#!/bin/sh

source ../env/bin/activate

TABLE_TYPE=$1
SUBSET=$2

python3 counts_table.py $TABLE_TYPE $SUBSET
