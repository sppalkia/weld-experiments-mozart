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
    # Get all city information with total population greater than 500,000
    data_big_cities = data[data["Total population"] > 500000]

    # Compute "crime index" proportional to
    # (Total population + 2*(Total adult population) - 2000*(Number of robberies)) / 100000
    data_big_cities_stats = data_big_cities[
        ["Total population", "Total adult population", "Number of robberies"]].values
    predictions = npw.dot(data_big_cities_stats, np.array(
        [1, 2, -2000], dtype=np.int64)) / 100000.0
    data_big_cities["Crime index"] = predictions

    # Aggregate "crime index" scores by state
    data_big_cities["Crime index"][data_big_cities["Crime index"] >= 0.02] = 0.032
    data_big_cities["Crime index"][data_big_cities["Crime index"] < 0.01] = 0.005
    return data_big_cities["Crime index"].sum().evaluate(num_threads=threads)

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

