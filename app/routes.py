from flask import Flask, render_template, flash, url_for, redirect, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditMovieForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Movie
from werkzeug.urls import url_parse
from datetime import datetime


@app.route("/")
@login_required
def home():
    return render_template("home.html")


@app.route("/movies")
@login_required
def movies():
    page = request.args.get("page", 1, type=int)
    movies = Movie.query.order_by(Movie.title.asc()).paginate(
        page, app.config["ITEMS_PER_PAGE"], False
    )
    next_url = url_for("movies", page=movies.next_num) if movies.has_next else None
    prev_url = url_for("movies", page=movies.prev_num) if movies.has_prev else None
    return render_template(
        "movies.html",
        movies=movies.items,
        page=page,
        next_url=next_url,
        prev_url=prev_url,
    )


@app.route("/movie/<id>")
@login_required
def movie(id):
    movie = Movie.query.get(id)
    if not movie:
        flash("Movie with id={} not found.".format(id))
        return redirect(url_for("movies"))
    return render_template("movie.html", movie=movie)


@app.route("/create_movie", methods=["GET", "POST"])
def movie_create():
    form = EditMovieForm()
    if form.validate_on_submit():
        movie = Movie(
            title=form.title.data,
            year=form.year.data,
            description=form.description.data,
            stars=form.stars.data,
        )
        db.session.add(movie)
        db.session.commit()
        flash("Movie {} added.".format(movie.title))
        return redirect(url_for("movie", id=movie.id))
    return render_template("movie_create.html", form=form)


@app.route("/movie/<id>/edit", methods=["GET", "POST"])
@login_required
def edit_movie(id):
    form = EditMovieForm()
    movie = Movie.query.get(id)
    if not movie:
        flash("Movie with id={} not found.".format(id))
        return redirect(url_for("movies"))
    if form.validate_on_submit():
        movie.title = form.title.data
        movie.year = form.year.data
        movie.description = form.description.data
        movie.stars = form.stars.data
        db.session.add(movie)
        db.session.commit()
        flash("Movie {} has been updated.".format(movie.title))
        return redirect(url_for("movie", id=movie.id))
    elif request.method == "GET":
        form.title.data = movie.title
        form.year.data = movie.year
        form.description.data = movie.description
        form.stars.data = movie.stars
    return render_template("movie_create.html", form=form)


@app.route("/actors")
@login_required
def actors():
    return render_template("actors.html")


@app.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("users.html", users=users)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("home"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)
