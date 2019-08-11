#!/bin/bash

source ../wedlbench/bin/activate

threads=( 1 2 4 8 16 )
runs=${1:-1}

rm -rf results/
mkdir results/

# Write system information.
git log | head -1 > results/CONFIG.txt
uname -a >> results/CONFIG.txt
lsb_release -d >> results/CONFIG.txt

mkdir -p results/birth_analysis
mkdir -p results/blackscholes
mkdir -p results/crime_index
mkdir -p results/data_cleaning
mkdir -p results/haversine
mkdir -p results/movielens
mkdir -p results/nbody
mkdir -p results/shallow_water

for i in {1..$runs}; do
  for nthreads in "${threads[@]}"; do
    # Birth Analysis
    python birth_analysis_grizzly.py -t $nthreads -f $HOME/composer/python/benchmarks/datasets/birth_analysis/_data/babynames-xlarge.txt >> results/birth_analysis/weld.stdout 2>> results/birth_analysis/weld.stderr 
    python blackscholes_weld.py -t $nthreads -s 30 >> results/blackscholes/weld.stdout 2>> results/blackscholes/weld.stderr 
    python crime_index_weld.py -t $nthreads -s 30 >> results/crime_index/weld.stdout 2>> results/crime_index/weld.stderr 
    python data_cleaning_weld.py -t $nthreads -s 29 >> results/data_cleaning/weld.stdout 2>> results/data_cleaning/weld.stderr 
    python haversine_weld.py -t $nthreads -s 30 >> results/haversine/weld.stdout 2>> results/haversine/weld.stderr 
    python movielens_grizzly.py -t $nthreads -f $HOME/composer/python/benchmarks/datasets/movielens/_data/ml-1m/ >> results/movielens/weld.stdout 2>> results/movielens/weld.stderr 
    # NOTE: These results should be run five times and summed, due to an OOM error in Weld.
    python nbody_weld.py -t $nthreads -s 15 -i 1 >> results/nbody/weld.stdout 2>> results/nbody/weld.stderr 
    # NOTE: These results should be run ten times and summed, due to an OOM error in Weld.
    python shallow_water_weld.py -t $nthreads -s 15 -i 1 >> results/shallo_water/weld.stdout 2>> results/shallow_water/weld.stderr 
  done
done

