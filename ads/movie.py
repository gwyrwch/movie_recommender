import os

import pandas


class Movie:
    def __init__(self, id, data):
        print(data)
        self.id = id
        self.title = data['title']
        print(self.title)
        # self.title = 'Toystory'
