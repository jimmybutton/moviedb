import json
from app import db
from app.models import Movie

def import_movies(movies):
    for m in movies:
        movie = Movie()                                                             
        for k, v in m.items():
            setattr(movie, k, v)
        movie.created_by=user
        db.session.add(movie)
    db.session.commit()

with open('../movies.json', "r") as fp:
    movies = json.load(fp)

import_movies(movies)