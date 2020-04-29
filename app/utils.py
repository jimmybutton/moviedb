import json

def delete_movies():
    movies = Movie.query.all()
    for m in movies:
        db.session.delete(m)
    db.session.commit()

def import_movies(movies):
    for m in movies:
        movie = Movie()                                                             
        for k, v in m.items():
            setattr(movie, k, v)
        movie.created_by=user
        db.session.add(movie)
    db.session.commit()

with open('movies.json', "r") as fp:
    movies = json.load(fp)

user = User.query.get(1)

delete_movies()
import_movies(movies)