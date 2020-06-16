from datetime import datetime
import json

user = User.query.get(1)

with open('scripts/actors.json','r',encoding='utf8') as fp:
  people = json.load(fp)

for p in people:
  person = People()                                                             
  for k, v in p.items():
    if k == 'movie_url':
      setattr(person, 'url', v)
    elif k == 'dob':
      # '1952-11-8'
      try:
        dob = datetime.strptime(v, '%Y-%m-%d').date()
        setattr(person, 'dob', dob)
      except ValueError as e:
        print(p['name'], e)
    else:
      setattr(person, k, v)
  person.created_by=user
  db.session.add(person)
  
db.session.commit()