from flask import Flask, render_template, flash, url_for, redirect, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime


@app.route("/")
@login_required
def home():
    movies = [
        {
            "title": "Parasite",
            "year": 2019,
            "desription": "A poor family, the Kims, con their way into becoming the servants of a rich family, the Parks. But their easy life gets complicated when their deception is threatened with exposure.",
            "director": "Bong Joon Ho",
            "actors": ["Kang-ho Song", "Sun-kyun Lee", "Yeo-jeong Jo"],
            "stars": 8.6,
        },
        {
            "title": "Inception",
            "year": 2010,
            "desription": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            "director": "Christopher Nolan",
            "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"],
            "stars": 8.8,
        },
        {
            "title": "Forrest Gump",
            "year": 1994,
            "desription": "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold through the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart.",
            "director": "Robert Zemeckis",
            "actors": ["Tom Hanks", "Robin Wright", "Gary Sinise"],
            "stars": 8.8,
        },
    ]
    return render_template("home.html", movies=movies)

@app.route("/movies")
@login_required
def movies():
    movies = [
        {
            "title": "Parasite",
            "year": 2019,
            "desription": "A poor family, the Kims, con their way into becoming the servants of a rich family, the Parks. But their easy life gets complicated when their deception is threatened with exposure.",
            "director": "Bong Joon Ho",
            "actors": ["Kang-ho Song", "Sun-kyun Lee", "Yeo-jeong Jo"],
            "stars": 8.6,
        },
        {
            "title": "Inception",
            "year": 2010,
            "desription": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            "director": "Christopher Nolan",
            "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"],
            "stars": 8.8,
        },
        {
            "title": "Forrest Gump",
            "year": 1994,
            "desription": "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold through the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart.",
            "director": "Robert Zemeckis",
            "actors": ["Tom Hanks", "Robin Wright", "Gary Sinise"],
            "stars": 8.8,
        },
    ]
    return render_template("movies.html", movies=movies)


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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)