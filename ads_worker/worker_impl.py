import os

import pandas
import numpy as np
from django.conf import settings


class Worker(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Worker, cls).__new__(cls)

            cls.instance.config = settings.CONFIG
            cls.instance.movie_vectors = pandas.read_csv(
                os.path.join(settings.BASE_DIR, cls.instance.config['movie_vec']), header=None, index_col=0
            )
        return cls.instance

    def calc_fit(self, user_vec, movie_vec):
        return (user_vec * movie_vec).sum()

    def recommend(self, user_vec):
        user_vec = np.array(user_vec)
        candidates = []
        for movie in self.config['movies']:
            id = movie['id']
            # print(id)
            movie_vec = self.movie_vectors.loc[id].to_numpy()
            # print(movie_vec)
            candidates.append(
                {
                    'movie_id': id,
                    'fit': self.calc_fit(user_vec, movie_vec)
                }
            )
        candidates.sort(key=lambda x: -x['fit'])
        if len(candidates) > 10:
            candidates = candidates[0:10]
        print(candidates)
        return {
            'candidates': candidates
        }