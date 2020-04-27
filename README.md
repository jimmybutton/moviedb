# moviedb
A flask based web application to search for movies and actors

## Features
- user login and authorization
- manage a list of movies and actors
- create, update and delete entries
- manage relationships (actors and roles in movies)
- search functionality for movies, movies by year, movies with actors etc.

### movie fields
- title
- year
- director
- description
- imdb rating
- (categories)

### actor fields
- name
- birthday
- bio

### association table
- actor
- role
- movie
- (money earned)

## ToDo
### Step 1
- DONE flesh out application structure, user model and movie model
- DONE create login and register page
- DONE create list view, details view and edit form for movies
- DONE display dates and times locally
- DONE order movies by columns
- DONE export movies to csv
- import movies from csv

### Step 2
- refactor using blueprints
- add a actor model
- list view, details view and edit form for actors
- add association table
- find a way to edit the relationsships

### Step 3
- filter and search for movies
- user comments on movies
