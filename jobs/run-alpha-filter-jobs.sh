#!/bin/bash

for i in {0..852}
do
    bash jobs/alpha-filter.submit $i
done
