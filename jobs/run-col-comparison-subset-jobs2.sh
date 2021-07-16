#!/bin/bash

SUBSET=$1

for i in {2131..4260}
do
    echo $i
    echo $SUBSET
    bash jobs/col-comparison-subset.submit $i $SUBSET
done
