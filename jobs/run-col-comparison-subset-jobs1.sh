#!/bin/bash

SUBSET=$1

for i in {0..2130}
do
    echo $i
    echo $SUBSET
    bash jobs/col-comparison-subset.submit $i $SUBSET
done
