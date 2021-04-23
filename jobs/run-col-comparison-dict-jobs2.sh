#!/bin/bash

for i in {3210..6418}
do
    echo $i
    bash jobs/col-comparison-dict.submit $i
done
