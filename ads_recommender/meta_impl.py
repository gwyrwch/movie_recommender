import json
import os
import time

import requests
import pandas as pd
import numpy as np

from scipy.sparse import lil_matrix
from scipy.sparse.linalg import svds

from django.conf import settings

from ads_recommender.movie_collection import MovieCollection

from threading import Thread


class Meta(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Meta, cls).__new__(cls)

            # Init
            cls.instance.config = settings.META_CONFIG
            cls.instance.user_vectors = pd.read_csv(
                os.path.join(settings.BASE_DIR, cls.instance.config['user_vec']), header=None, index_col=0
            )
            cls.instance.special_list = [
                MovieCollection().get_movie(id)
                for id in [211672,19995,321612,297762,283995,177572,155,271110,293660,24428,140607,131631,166426,597,99861,210577,337339,168259,135397,12445,119450,339403,122,118340,330459,109445,671,11,68721,13,281338,58,269149,121,120,324852,122917,49026,259316,680,285,263115,12,27205,1865,37724,672,49051,12444,22,10193,93456,674,57158,150540,675,673,284052,101299,157336,767,557,91314,12155,8587,127380,297761,278927,209112,127585,559,206647,1930,809,50620,601,76338,1893,14160,602,24021,286217,102651,329,100402,1895,102382,198663,8355,335988,38356,49047,57800,591,745,18239,411,131634,62211,9806,70160,50619,61791,585,374720,2062,604,603,177677,328111,36557,810,1726,14161,558,80321,335797,49521,1891,56292,293167,217,280,281957,102899,9502,950,10138,246655,10192,20352,72190,372058,424,190859,1892,857,216015,38757,87827,82702,1894,98,74,49444,607,12092,8373,615,254,150689,10681,207703,49519,277834,18785,1593,72105,10195,137113,68726,578,313369,863,812,105,1858,62177,808,10527,6479,10528,129,41154,8960,118,955,953,10764,11631,616,245891,8358,272,76341,68718,35,10191,137106,95,435,140300,89,82992,652,87101,54138,77338,238,2503]
            ]
        return cls.instance

    def get_special_list(self):
        return self.special_list

    def request_worker(self, addr, shard, shard_responsed, candidates, my_vector):
        try:
            response = requests.get(addr + '/worker/', json={
                'user_vec': my_vector.tolist()
            })
            if response.status_code == 200:
                if not shard in shard_responsed:
                    shard_responsed.add(shard)
                    for cand in response.json()['candidates']:
                        candidates.append({
                            'movie': cand['movie_id'],
                            'fit': cand['fit']
                        })
        except Exception as e:
            print(e)
            pass

    def calc_candidates(self, uid):
        """
            main function to predict movie for uid
        """
        if not uid in self.user_vectors.index:
            return []
        my_vector = self.user_vectors.loc[uid]
        candidates = []
        print(my_vector)
        shard_responsed = set()

        threads = []
        for worker in self.config['workers']:
            addr = worker['address']
            shard = worker['shard']
            t = Thread(target=self.request_worker, args=(addr, shard, shard_responsed, candidates, my_vector))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        candidates.sort(key=lambda x: -x['fit'])
        if len(candidates) > 10:
            candidates = candidates[:10]

        for i in range(len(candidates)):
            candidates[i]['movie'] = MovieCollection().get_movie(candidates[i]['movie'])
        print(candidates)

        return list(map(lambda x: x['movie'], candidates))

    def create_user(self, id, movies):
        now = int(time.time())
        with open('movies/ratings_up.csv', 'a') as f:
            for m in movies:
                f.write('{},{},5.0,{}\n'.format(id, m, now))
        self.train_svd()
        self.reload_vectors()

    def train_svd(self):
        print('started training svd')
        uvec_path = os.path.join(settings.BASE_DIR, self.config['user_vec'])

        ratings = pd.read_csv('movies/ratings_up.csv')
        users_count = ratings.userId.max()
        A = lil_matrix((users_count, 45466))

        print('Total users', users_count)

        movies = pd.read_csv('movies/movies_metadata.csv')
        ratings.rename(columns={'movieId': 'id'}, inplace=True)
        ratings['id'] = ratings['id'].astype(str)
        movies['id'] = movies['id'].astype(str)
        movies = movies[movies.id != '1997-08-20']
        movies = movies[movies.id != '2012-09-29']
        movies = movies[movies.id != '2012-09-29']
        movies = movies[movies.id != '2014-01-01']
        movies.id = movies.id.astype(int)

        print('Read input')

        mids = {}
        whichMid = {}

        for i, mid in zip(movies.id.index, movies.id.values):
            if mid in mids:
                continue
            mids[mid] = i
            whichMid[i] = mid

        print('Prepared mapping')

        for i in range(len(ratings)):
            rate = ratings.iloc[i]
            uid = int(rate['userId'] + 0.1)
            mid = int(rate['id'])
            if mid in mids:
                rating = rate['rating']
                A[uid - 1, mids[mid]] = rating - 2.5
        print('Prepared matrix A')

        u, s, vt = svds(A, k=100)  # k is the number of factors

        print('trained svd')

        udf = pd.DataFrame(u)
        udf['id'] = udf.index + 1
        cols = list(udf.columns)
        cols.pop()
        cols = ['id'] + cols
        udf = udf[cols]
        udf.head()

        udf.to_csv(uvec_path, header=None, index=False)

        print('Done')

    def reload_vectors(self):
        self.user_vectors = pd.read_csv(
            os.path.join(settings.BASE_DIR, self.config['user_vec']), header=None, index_col=0
        )
