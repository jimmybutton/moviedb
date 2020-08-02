from app import db, login
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import sqlalchemy as sa


class BaseModel(object):
    @classmethod
    def _get_keys(cls):
        return sa.orm.class_mapper(cls).c.keys()

    def to_dict(self):
        d = {}
        for k in self._get_keys():
            value = getattr(self, k)
            if isinstance(value, datetime.datetime):
                d[k] = value.isoformat()
            else:
                d[k] = value
        return d


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    created_timestamp = db.Column(
        db.DateTime, index=True, default=datetime.datetime.utcnow
    )
    created_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_by = db.relationship("User", foreign_keys=[created_id])
    modified_timestamp = db.Column(
        db.DateTime,
        index=True,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    modified_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    modified_by = db.relationship("User", foreign_keys=[modified_id])

    title = db.Column(db.String(128), index=True)
    year = db.Column(db.Integer)
    director = db.Column(db.String(64))
    category = db.Column(db.String(64))
    certificate = db.Column(db.String(16))
    release_date = db.Column(db.String(128))
    plot_summary = db.Column(db.Text())
    rating_value = db.Column(db.Float)
    rating_count = db.Column(db.Integer)
    poster_url = db.Column(db.String(256))
    runtime = db.Column(db.Integer)
    url = db.Column(db.String(64))

    cast = db.relationship(
        "Character", foreign_keys="Character.movie_id", backref="movie", lazy="dynamic"
    )

    def __repr__(self):
        return "<Movie {}>".format(self.title)

    @property
    def displayname(self):
        return f"{self.title} ({self.year})"

    @property
    def default_image_url(self):
        if self.poster_url:
            return self.poster_url
        else:
            return "https://m.media-amazon.com/images/G/01/imdb/images/nopicture/small/film-293970583._CB469775754_.png"


class People(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    created_timestamp = db.Column(
        db.DateTime, index=True, default=datetime.datetime.utcnow
    )
    created_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_by = db.relationship("User", foreign_keys=[created_id])
    modified_timestamp = db.Column(
        db.DateTime,
        index=True,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    modified_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    modified_by = db.relationship("User", foreign_keys=[modified_id])

    name = db.Column(db.String(64), index=True)
    url = db.Column(db.String(64))
    image_url = db.Column(db.String(256))
    dob = db.Column(db.Date())
    birthname = db.Column(db.String(128))
    height = db.Column(db.String(64))
    bio = db.Column(db.Text())

    roles = db.relationship(
        "Character", foreign_keys="Character.actor_id", backref="actor", lazy="dynamic"
    )

    def __repr__(self):
        return "<Person {}>".format(self.name)

    @property
    def default_image_url(self):
        if self.image_url:
            return self.image_url
        else:
            return "https://m.media-amazon.com/images/G/01/imdb/images/nopicture/32x44/name-2138558783._CB468460248_.png"


class Character(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    created_timestamp = db.Column(
        db.DateTime, index=True, default=datetime.datetime.utcnow
    )
    created_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_by = db.relationship("User", foreign_keys=[created_id])
    modified_timestamp = db.Column(
        db.DateTime,
        index=True,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    modified_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    modified_by = db.relationship("User", foreign_keys=[modified_id])

    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))
    actor_id = db.Column(db.Integer, db.ForeignKey("people.id"))
    character_name = db.Column(db.String(128))
    character_url = db.Column(db.String(128))
    order = db.Column(db.Integer)  # order in which to show character per movie

    @property
    def actor_name(self):
        return self.actor.name

    def __repr__(self):
        return "<Character {}, Actor {}, Movie {}, Order {}>".format(
            self.character_name, self.actor.name, self.movie.title, self.order
        )

    def to_dict(self):
        d = super().to_dict()
        d.update({
                "movie_title": self.movie.title,
                "movie_image": self.movie.default_image_url,
                "movie_year": self.movie.year,
                "actor_name": self.actor.name,
                "actor_image": self.actor.default_image_url,
            })
        return d


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
