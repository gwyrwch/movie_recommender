import json
import os

import requests
import pandas

from django.conf import settings

from ads.movie import Movie
from ads_recommender.movie_collection import MovieCollection


class Meta(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Meta, cls).__new__(cls)

            # Init
            cls.instance.config = settings.META_CONFIG
            cls.instance.user_vectors = pandas.read_csv(
                os.path.join(settings.BASE_DIR, cls.instance.config['user_vec']), header=None, index_col=0
            )
        return cls.instance

    def get_worker_address(self):
        return list(map(lambda x: x['address'], self.config['workers']))

    def calc_candidates(self, uid):
        """
            main function to predict movie for uid
        """
        my_vector = self.user_vectors.loc[uid]
        candidates = []

        for addr in self.get_worker_address():
            response = requests.get(addr + '/worker/', json={
                'user_vec': my_vector.tolist()
            })
            if response.status_code == 200:
                for cand in response.json()['candidates']:
                    movie = MovieCollection().get_movie(cand['movie_id'])
                    if movie is not None:
                        candidates.append({
                            'movie': movie,
                            'fit': cand['fit']
                        })
        candidates.sort(key=lambda x: -x['fit'])
        if len(candidates) > 10:
            candidates = candidates[:10]
        return list(map(lambda x: x['movie'], candidates))
