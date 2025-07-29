#!/bin/sh
./results.py round* > results.csv
split -l 9 --additional-suffix=.csv results.csv results-
mv results-aa.csv requests.csv
mv results-ab.csv latencies.csv
mv results-ac.csv cpu.csv
mv results-ad.csv memory.csv
mv results-ae.csv errors.csv
sed -i -n '3,$p' requests.csv
sed -i -n '3,$p' latencies.csv
sed -i -n '3,$p' cpu.csv
sed -i -n '3,$p' memory.csv
sed -i -n '3,$p' errors.csv
python plotresults.py
