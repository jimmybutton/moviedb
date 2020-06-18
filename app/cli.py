from app.models import User, Movie, People, Character
from datetime import datetime
import json
from app import db
from flask import Blueprint

bp = Blueprint('cli', __name__, cli_group=None)

@bp.cli.command("import-cast")
def import_cast():
  """import characters for cast.json file"""
  url_prefix = "https://www.imdb.com"

  user = User.query.get(1)
  print(user)

  with open('data/cast.json','r',encoding='utf8') as fp:
    movies = json.load(fp)
  
  for m in movies[69:]:
    movie_url = m.get('movie_url')
    movie = Movie.query.filter_by(url=movie_url).first()
    if not movie:
      print(f"ERROR movie {m.get('title')} not found.")
    else:
      print(movie)
    for i, c in enumerate(m.get('cast')):
      if c.get('actor_url'):
        actor_url = url_prefix + c.get("actor_url")
        actor = People.query.filter_by(url=actor_url).first()
        if actor:
          pass
        else:
          print(f"ERROR actor {c.actor} not found.")
      character_name = c.get("role")
      char = None
      if movie and actor:
        # check if character exists
        # movie_id, actor_id and character_name need to match
        char = Character.query.filter_by(movie_id=movie.id, actor_id=actor.id, character_name=character_name).first()
      if char:
        edit_mode = 'update'
      else:
        edit_mode = 'create'
        # if it doesnt exists, create a new one
        char = Character(created_by=user)
      char.order = i
      char.modified_by = user
      character_url = url_prefix + c.get("role_url") if c.get("role_url") else None
      if character_url:
        char.character_url = character_url
      char.character_name = character_name
      if movie:
        char.movie = movie
        char.movie_title = movie.title
        char.movie_year = movie.year
      else:
        char.movie_title = m.get('title')
      if actor:
        char.actor = actor
        char.actor_name = actor.name
      else:
        char.actor_name = c.get('actor')

      db.session.add(char)
      db.session.commit()

      print(f"{edit_mode}d {char}")