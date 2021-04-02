#!/bin/bash

SUBSET=$1
MEM=$2

for i in {0..3999}
do
    echo $i
    echo $SUBSET
    echo $MEM
    bash jobs/col-comparison-subset.submit $i $SUBSET $MEM
done
