import json
import os

import requests
import pandas

from django.conf import settings

from ads.movie import Movie
from ads_recommender.movie_collection import MovieCollection

from threading import Thread

class Meta(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Meta, cls).__new__(cls)

            # Init
            cls.instance.config = settings.META_CONFIG
            cls.instance.user_vectors = pandas.read_csv(
                os.path.join(settings.BASE_DIR, cls.instance.config['user_vec']), header=None, index_col=0
            )
            cls.instance.special_list = [
                MovieCollection().get_movie(id)
                for id in [211672,19995,321612,297762,283995,177572,155,271110,293660,24428,140607,131631,166426,597,99861,210577,337339,168259,135397,12445,119450,339403,122,118340,330459,109445,671,11,68721,13,281338,58,269149,121,120,324852,122917,49026,259316,680,285,263115,12,27205,1865,37724,672,49051,12444,22]
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
