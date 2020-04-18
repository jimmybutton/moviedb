# moviedb
A flask based web application to search for movies and actors

## Features
- manage a list of movies and actors in a database
- create, update and delete entries
- manage relationships (actors and roles in movies)
- advanced search functionalities for movies, movies by year, movies with actors etc.
- have a user login and authorization

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
- flesh out application structure, user model and movie model
- create login and register page
- create list view, details view and edit form for movies

### Step 2
- add a actor model
- list view, details view and edit form for actors
- add association table
- find a way to edit the relationsships

### Step 3
- filter and search for movies
