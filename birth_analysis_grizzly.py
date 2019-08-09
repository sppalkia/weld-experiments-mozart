from __future__ import print_function

import pandas as pd
import grizzly.grizzly as gr
import numpy as np
import time
import sys

import argparse

import warnings
warnings.filterwarnings('ignore')

def get_top1000(group):
    return group.sort_values(by='births', ascending=False).slice(0, 1000)

def analyze(top1000, threads):
    start1 = time.time()
    top1000 = gr.DataFrameWeld(top1000)
    top1000names = top1000['name']
    all_names = top1000names.unique()
    lesley_like = all_names.filter(all_names.lower().contains('lesl'))

    filtered = top1000.filter(top1000names.isin(lesley_like))
    table = filtered.pivot_table('births', index='year',
                                  columns='sex', aggfunc='sum')

    table = table.div(table.sum(1), axis=0)
    end1 = time.time()
    result = table.evaluate(True, workers=threads).to_pandas()
    return result

def run(filename, threads):
    years = range(1880, 2011)
    columns = ['year', 'sex', 'name', 'births']

    sys.stdout.write("Reading data...")
    sys.stdout.flush()
    names = pd.read_csv(filename, names=columns)
    print("done.")
    sys.stdout.flush()
    print("Size of names:", len(names))

    # Time preprocessing step
    # This is a weird effect where the cols are being unnecessarily copied...?
    start = time.time()
    grouped = gr.DataFrameWeld(names)
    end = time.time()
    print("DF Weld time:", end - start)
    
    e2e_start = time.time()
    grouped = grouped.groupby(['year', 'sex'])
    top1000 = grouped.apply(get_top1000)
    # Drop the group index, not needed
    top1000.reset_index(inplace=True, drop=True)
    top1000 = top1000.evaluate(True, workers=threads).to_pandas()

    # result = analyze(top1000)

    e2e_end = time.time()
    print("Total time:", e2e_end - e2e_start)

    print(top1000['births'].sum())

def main():
    parser = argparse.ArgumentParser(
        description="Birth Analysis with the almighty Grizzly."
    )
    parser.add_argument('-f', "--filename", type=str, default="babynames.txt", help="Input file")
    parser.add_argument('-t', "--threads", type=int, default=1, help="Number of threads")
    args = parser.parse_args()

    filename = args.filename
    threads = args.threads

    print("File:", filename)
    print("Threads:", threads)
    mi = run(filename, threads)


if __name__ == "__main__":
    main()
