import os

import pandas
import json


class Movie:
    def __init__(self, id, data):
        print(data)
        self.id = id
        self.title = data['title']
        self.genres = []
        genres = json.loads("[{'id': 28, 'name': 'Action'}]".replace('\'', '"'))
        if genres == list:
            for d in genres:
                if 'name' in d:
                    self.genres.append(d['name'])

        self.overview = data['overview']
        self.popularity = data['popularity']
        self.release_date = data['release_date']
        self.runtime = data['runtime']
        self.tagline = data['tagline']
        self.vote_average = data['vote_average']

