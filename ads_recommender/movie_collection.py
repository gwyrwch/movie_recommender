import os

import pandas
import requests
from django.conf import settings

from ads.movie import Movie


class MovieCollection:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MovieCollection, cls).__new__(cls)
            cls.instance.movies = pandas.read_csv(
                os.path.join(settings.BASE_DIR, 'movies/movies_metadata.csv')
            )
            cls.instance.movies['id'] = cls.instance.movies['id'].astype(str)
            cls.instance.movies = cls.instance.movies[cls.instance.movies.id != '1997-08-20']
            cls.instance.movies = cls.instance.movies[cls.instance.movies.id != '2012-09-29']
            cls.instance.movies = cls.instance.movies[cls.instance.movies.id != '2012-09-29']
            cls.instance.movies = cls.instance.movies[cls.instance.movies.id != '2014-01-01']
            cls.instance.movies.id = cls.instance.movies.id.astype(int)
            cls.instance.movies = cls.instance.movies.set_index('id')
            cls.session = requests.Session()
            cls.session.trust_env = False

        return cls.instance

    def get_movie(self, id):
        try:
            return Movie(id, self.movies.loc[id], self.session)
        except KeyError as e:
            print(e)
            return None

