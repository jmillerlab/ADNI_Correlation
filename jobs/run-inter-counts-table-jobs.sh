#!/bin/bash

TABLE_TYPE=$1
SUBSET=$2

for i in {0..1293}
do
    echo $i
    echo $TABLE_TYPE
    echo $SUBSET
    bash jobs/inter-counts-table.submit $i $TABLE_TYPE $SUBSET
done
