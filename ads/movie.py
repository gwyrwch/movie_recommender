import json


class Movie:
    def __init__(self, id, data, session):
        # print(data)
        self.id = id
        self.title = data['title']
        self.genres = []
        genres = json.loads(data['genres'].replace('\'', '"'))
        if type(genres) == list:
            for d in genres:
                if 'name' in d:
                    self.genres.append(d['name'])

        self.overview = data['overview']
        self.popularity = data['popularity']

        self.release_date = data['release_date']
        self.runtime = data['runtime']
        self.tagline = data['tagline']

        if type(self.tagline) != str:
            self.tagline = ''

        self.vote_average = data['vote_average']

        # path = '/qcr9bBY6MVeLzriKCmJOv1562uY.jpg'
        path = data['poster_path']

        path = session.get('https://api.themoviedb.org/3/movie/{}?api_key=5f36548499df4226feac1ab5f1fa2e45'.format(id)).json()['poster_path']

        self.poster_path = 'https://image.tmdb.org/t/p/original{}'.format(path)
        print(self.poster_path)

