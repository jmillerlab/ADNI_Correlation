bash jobs/sig-freqs-summary.sh maximum 100 data/maximum-sig-freqs.csv true
bash jobs/sig-freqs-summary.sh bonferroni 100 data/bonferroni-sig-freqs.csv false
bash jobs/sig-freqs-summary.sh male 100 data/male-sig-freqs.csv true
bash jobs/sig-freqs-summary.sh female 100 data/female-sig-freqs.csv true
bash jobs/sig-freqs-summary.sh 0.0 100 data/0.0-sig-freqs.csv true
bash jobs/sig-freqs-summary.sh 0.5 100 data/0.5-sig-freqs.csv true
bash jobs/sig-freqs-summary.sh 1.0 100 data/1.0-sig-freqs.csv true
