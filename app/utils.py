import json
import csv
from io import StringIO
from datetime import datetime

def export_csv(items, fields):
    """
    Generate the data with csv.writer and stream the response. 
    Use StringIO to write to an in-memory buffer rather than 
    generating an intermediate file.
    """
    data = StringIO()
    w = csv.writer(data)
    w.writerow(fields)  # header
    for i in items:
        w.writerow([getattr(i, field) for field in fields])
    return data.getvalue()



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

def import_people(people):
    for p in people:
        person = People()                                                             
        for k, v in p.items():
            if k == 'movie_url':
                setattr(person, 'url', v)
            elif k == 'dob':
                # '1952-11-8'
                dob = datetime.strptime(v, '%Y-%m-%d').date()
                setattr(person, 'dob', dob)
            else:
                setattr(person, k, v)
        db.session.add(person)
    db.session.commit()

def paginate(current_page=1, total_pages=10, num_links=5):
    m = total_pages
    n = current_page
    l = int((num_links - 1) / 2)  # number of page links to left and right

    if n <= 0 or n > m:
        raise ValueError(f'Current page {n} out of total page range {m}')

    if m < num_links:
        return list(range(1, m+1))
    else:
        if n <= l:
            return list(range(1, 2*l + 2))
        elif n > l and n <= m - l:
            return list(range(n - l, n + l + 1))
        elif n > m - l:
            return list(range(m - 2 * l, m+1))

if __name__ == "__main__":
    with open('movies.json', "r") as fp:
        movies = json.load(fp)

    user = User.query.get(1)

    delete_movies()
    import_movies(movies)