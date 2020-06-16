from app.models import User, Movie, People, Character
from datetime import datetime
import json

def import_cast():
  url_prefix = "https://www.imdb.com"

  user = User.query.get(1)
  print(user)

  with open('data/cast.json','r',encoding='utf8') as fp:
    movies = json.load(fp)
  
  for m in movies:
    movie_url = m.get('movie_url')
    movie = Movie.query.filter_by(url=movie_url).first()
    if not movie:
      print(f"ERROR movie {m.get('title')} not found.")
    else:
      print(movie)
    for c in m.get('cast'):
      if c.get('actor_url'):
        actor_url = url_prefix + c.get("actor_url")
        actor = People.query.filter_by(url=actor_url).first()
        if actor:
          print(actor)
        else:
          print(f"ERROR actor {c.actor} not found.")
      char = Character()
      char.character_url = url_prefix + c.get("role_url") if c.get("role_url") else None,
      char.character_name = c.get("role")
      if movie:
        char.movie = movie
        char.movie_title = movie.title
        char.movie_year = movie.year
      else:
        char.movie_title = m.title
      if actor:
        char.actor = actor
        char.actor_name = actor.name
      else:
        char.actor_name = c.get('actor')  
      char.created_by = user
      print(char)

# for p in people:
#   person = People()                                                             
#   for k, v in p.items():
#     if k == 'movie_url':
#       setattr(person, 'url', v)
#     elif k == 'dob':
#       # '1952-11-8'
#       try:
#         dob = datetime.strptime(v, '%Y-%m-%d').date()
#         setattr(person, 'dob', dob)
#       except ValueError as e:
#         print(p['name'], e)
#     else:
#       setattr(person, k, v)
#   person.created_by=user
#   db.session.add(person)
  
# db.session.commit()