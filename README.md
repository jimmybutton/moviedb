# moviedb
A web application based on flask and boostrap 4 to browse movies, actors and directors, manage a watchlist, write reviews etc.

## Features
- user login and authorization
- manage a list of movies and actors
- create, update and delete entries
- manage relationships (actors and roles in movies)
- search functionality for movies and actors etc.
- manage a watchlist
- write reviews and rate movies

### movie fields
- title
- year
- director
- description
- imdb rating
- (categories)

### people fields
- name
- birthday
- bio

### association table
- actor
- role
- movie
- order

## ToDo
### Step 1
- DONE flesh out application structure, user model and movie model
- DONE create login and register page
- DONE create list view, details view and edit form for movies
- DONE order movies by columns

### Step 2
- DONE refactor using blueprints
- DONE add a actor model
- list view, details view and edit form for actors
- filter and search for movies
- DONE add association table
- edit form for association table
- users can add and remove movies to / from their watchlist
- display dates and times locally

### Step 3
- user comments and ratings on movies
- authorization (users can view, manage watchlist and write reviews, admins can edit and delete movies and actors)
- export movies etc. to csv/json
- import movies etc. from csv/json
