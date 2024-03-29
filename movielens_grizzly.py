import argparse

import pandas as pd
import grizzly.grizzly as gr
import time

import warnings
warnings.filterwarnings('ignore')

# Make display smaller
pd.options.display.max_rows = 10

def get_data(path):
    unames = ['user_id', 'gender', 'age', 'occupation', 'zip']
    users = pd.read_table(path + 'users.dat', sep='::', header=None,
                          names=unames)

    rnames = ['user_id', 'movie_id', 'rating', 'timestamp']
    ratings = pd.read_table(path + 'ratings.dat', sep='::', header=None,
                            names=rnames)

    mnames = ['movie_id', 'title', 'genres']
    movies = pd.read_table(path + 'movies.dat', sep='::', header=None,
            names=mnames, dtype={'movie_id': 'int64', 'title': 'str', 'genres': 'str'})
    return users, ratings, movies

def movielens(users, ratings, movies, threads):
    start = time.time()
    ratings = gr.DataFrameWeld(ratings)
    users = gr.DataFrameWeld(users)
    movies = gr.DataFrameWeld(movies)

    data = gr.merge(gr.merge(ratings, users), movies).evaluate(workers=threads).to_pandas()
    end = time.time()

    start1 = time.time()
    data = gr.DataFrameWeld(data)
    data = data[data['age'] > 45]
    mean_ratings = data.pivot_table('rating', index='title', columns='gender',
                                    aggfunc='mean')


    ratings_by_title = data.groupby('title').size()
    active_titles = ratings_by_title.index[ratings_by_title >= 250]
    mean_ratings = mean_ratings.loc[active_titles]
    mean_ratings['diff'] = mean_ratings['M'] - mean_ratings['F']
    sorted_by_diff = mean_ratings.sort_values(by='diff')
    rating_std_by_title = data.groupby('title')['rating'].std()
    rating_std_by_title = rating_std_by_title.loc[active_titles]
    rating_std_by_title = rating_std_by_title.sort_values(ascending=False)[0:10]
    sorted_by_diff, rating_std_by_title = gr.group_eval([sorted_by_diff, rating_std_by_title])
    end1 = time.time()

    print "Time to merge:", (end - start)
    print "Time for analysis:", (end1 - start1)
    print "Total:", end1 - start
    return rating_std_by_title

def main():
    parser = argparse.ArgumentParser(
        description="MovieLens with the almighty Grizzly."
    )
    parser.add_argument('-t', "--threads", type=int, default=1, help="Number of threads")
    parser.add_argument('-f', "--filename", type=str, default="./", help="Directory with data")
    args = parser.parse_args()

    threads = args.threads
    filename = args.filename

    print("Threads:", threads)
    print("Filename:", filename)
    users, ratings, movies = get_data(filename)
    rating_std_by_title = movielens(users, ratings, movies, threads)
    print rating_std_by_title

if __name__ == "__main__":
    main()
