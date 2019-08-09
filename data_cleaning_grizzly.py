#!/usr/bin/python

import argparse
import pandas as pd
import grizzly.grizzly as gr
import sys
import time

def gen_data(size):
    values = ["1234567" for  _ in range(size)]
    return gr.DataFrameWeld(pd.DataFrame(data={'Incident Zip': values}))

def data_cleaning_weld(requests, threads):
    # Fix requests with extra digits
    requests['Incident Zip'] = requests['Incident Zip'].str.slice(0, 5)
    # Fix requests with 00000 zipcodes
    zero_zips = requests['Incident Zip'] == '00000'
    requests['Incident Zip'][zero_zips] = "nan"
    # Display unique incident zips again (this time cleaned)
    return requests['Incident Zip'].unique().evaluate(workers=threads)

def run():
    parser = argparse.ArgumentParser(
        description="Data Cleaning"
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
    result = data_cleaning_weld(inputs, threads)
    end = time.time()
    print(end - start, "seconds")
    print(result)

if __name__ == "__main__":
    run()

