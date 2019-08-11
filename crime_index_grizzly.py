#!/usr/bin/python

import argparse
import sys

# The usual preamble
import numpy as np
import grizzly.numpy_weld as npw
import pandas as pd
import grizzly.grizzly as gr
import time

def gen_data(size):
    total_population = np.ones(size, dtype="float64") * 500000
    adult_population = np.ones(size, dtype="float64") * 250000
    num_robberies = np.ones(size, dtype="float64") * 1000
    return gr.DataFrameWeld(
            pd.DataFrame(data= {
                "Total population": total_population,
                "Total adult population": adult_population,
                "Number of robberies": num_robberies,
                }))

def crime_index_weld(data, threads):
    total_population = data["Total population"]
    adult_population = data["Total adult population"]
    num_robberies = data["Number of robberies"]
    big_cities = total_population > 500000
    big_cities = total_population.mask(big_cities, 0.0)
    double_pop = ((adult_population * 2.0) + big_cities).sub(num_robberies * 2000.0)
    crime_index = double_pop / 100000.0
    crime_index = crime_index.mask(crime_index > 0.02, 0.032)
    crime_index = crime_index.mask(crime_index < 0.01, 0.005)
    return crime_index.sum().evaluate(num_threads=threads)

def run():
    parser = argparse.ArgumentParser(
        description="Crime Index"
    )
    parser.add_argument('-s', "--size", type=int, default=26, help="Size of each array")
    parser.add_argument('-t', "--threads", type=int, default=1, help="Number of threads.")
    args = parser.parse_args()

    size = (1 << args.size)
    threads = args.threads

    assert threads >= 1

    print("Size:", size)
    print("Threads:", threads)

    sys.stdout.write("Generating data...")
    sys.stdout.flush()
    inputs = gen_data(size)
    print("done.")
    sys.stdout.flush()

    start = time.time()
    result = crime_index_weld(inputs, threads)
    end = time.time()
    print(end - start, "seconds")
    print(result)

if __name__ == "__main__":
    run()

