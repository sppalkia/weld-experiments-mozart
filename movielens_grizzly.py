import pandas as pd
import grizzly.grizzly as gr
import time

import warnings
warnings.filterwarnings('ignore')

# Make display smaller
pd.options.display.max_rows = 10

unames = ['user_id', 'gender', 'age', 'occupation', 'zip']
users = pd.read_table('~/composer/python/benchmarks/datasets/movielens/_data/ml-1m/users.dat', sep='::', header=None,
                      names=unames)

rnames = ['user_id', 'movie_id', 'rating', 'timestamp']
ratings = pd.read_table('~/composer/python/benchmarks/datasets/movielens/_data/ml-1m/ratings.dat', sep='::', header=None,
                        names=rnames)

mnames = ['movie_id', 'title', 'genres']
movies = pd.read_table('~/composer/python/benchmarks/datasets/movielens/_data/ml-1m/movies.dat', sep='::', header=None,
        names=mnames, dtype={'movie_id': 'int64', 'title': 'str', 'genres': 'str'})

start = time.time()
ratings = gr.DataFrameWeld(ratings)
users = gr.DataFrameWeld(users)
movies = gr.DataFrameWeld(movies)

data = gr.merge(gr.merge(ratings, users), movies).evaluate(True, threads=8).to_pandas()
end = time.time()

fstart = time.time()
data = gr.DataFrameWeld(data)
data = data[data['age'] > 45]
data = data.evaluate(True, threads=8).to_pandas()
fend = time.time()
print "Filter:", fend - fstart

start1 = time.time()
print data
data = gr.DataFrameWeld(data)
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

print sorted_by_diff
print rating_std_by_title
print "Time to merge:", (end - start)
print "Time for analysis:", (end1 - start1)
