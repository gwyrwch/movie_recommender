import os

import pandas
from django.conf import settings

from ads.movie import Movie


class MovieCollection:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MovieCollection, cls).__new__(cls)
            cls.instance.movies = pandas.read_csv(
                os.path.join(settings.BASE_DIR, 'movies/movies_metadata.csv')
            ).set_index('id')
        return cls.instance

    def get_movie(self, id):
        try:
            return Movie(id, self.movies.loc[str(id)])
        except KeyError:
            return None

