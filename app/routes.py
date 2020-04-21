from flask import Flask, render_template, flash, url_for, redirect
from app import app
from app.forms import LoginForm



@app.route("/")
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


@app.route("/actors")
def actors():
    return render_template("actors.html")


@app.route("/users")
def users():
    return render_template("users.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.username.data, form.remember_me.data
            )
        )
        return redirect(url_for("home"))
    return render_template("login.html", form=form)

