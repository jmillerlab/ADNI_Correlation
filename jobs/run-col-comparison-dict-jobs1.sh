#!/bin/bash

for i in {0..3209}
do
    echo $i
    bash jobs/col-comparison-dict.submit $i
done
