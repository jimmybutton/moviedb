from app import db, login
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.search import (
    add_to_index,
    remove_from_index,
    query_index,
    query_index_full_text,
    clear_index,
)
import progressbar


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        """full text search across all search in __searchable__"""
        ids, total = query_index_full_text(
            cls.__tablename__, expression, page, per_page
        )
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = [(ids[i], i) for i in range(len(ids))]
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)),
            total,
        )

    @classmethod
    def search_query(cls, query, page, per_page, sort_by=None, order="asc"):
        """allows for complex queries with elasticsearch dsl"""
        ids, total = query_index(
            cls.__tablename__, query, page, per_page, sort_by, order
        )
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = [(ids[i], i) for i in range(len(ids))]  # sort by search score
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)),
            total,
        )

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        clear_index(cls.__tablename__, cls.__searchable__)
        for obj in progressbar.progressbar(cls.query, max_value=cls.query.count()):
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)


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


class Movie(SearchableMixin, db.Model):
    __searchable__ = {
        "id": {"type": "keyword"},
        "title": {
            "type": "text",
            "fields": {"raw": {"type":  "keyword"}}},  # later add a search_as_you_type field
        "year": {"type": "short"},
        "director": {
            "type": "text",
            "fields": {"raw": {"type":  "keyword"}}},
        "category": {"type": "keyword"},
        "certificate": {"type": "keyword"},
        "release_date": {"type": "text"},  # this should be date and needs to be cleaned!
        "plot_summary": {"type": "text"},
        "rating_value": {"type": "short"},
        "rating_count": {"type": "integer"},
        "runtime": {"type": "short"},
    }
    __default_sort__ = ("rating_value", "desc")
    __formfields__ = [
        "title",
        "year",
        "director",
        "category",
        "certificate",
        "release_date",
        "plot_summary",
        "rating_value",
        "rating_count",
        "poster_url",
        "runtime",
        "url",
    ]
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
    plot_summary = db.Column(db.String(512))
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

    def to_dict(self):
        fields = ["id", "modified_timestamp"] + self.__formfields__
        data = {}
        for f in fields:
            data[f] = getattr(self, f)
        return data


class People(SearchableMixin, db.Model):
    __searchable__ = {
        "id": {"type": "keyword"},
        "modified_timestamp": {"type": "date"},
        "name": {
            "type": "text",
            "fields": {"raw": {"type":  "keyword"}}},
        "bio": {"type": "text"},
        "dob": {"type": "date"}
    }
    __default_sort__ = ("name.raw", "asc")
    __formfields__ = ["name", "url", "image_url", "dob", "birthname", "height", "bio"]
    _image_url_fallback = "https://m.media-amazon.com/images/G/01/imdb/images/nopicture/32x44/name-2138558783._CB468460248_.png"
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
    bio = db.Column(db.String(1024))

    roles = db.relationship(
        "Character", foreign_keys="Character.actor_id", backref="actor", lazy="dynamic"
    )

    def __repr__(self):
        return "<Person {}>".format(self.name)

    def to_dict(self):
        fields = ["id", "modified_timestamp"] + self.__formfields__
        data = {}
        for f in fields:
            value = getattr(self, f)
            if f == "image_url" and value is None:
                value = self._image_url_fallback
            if type(value) is datetime.date:
                data[f] = value.strftime(r"%a, %d %b %Y")
            else:
                data[f] = value
        return data


class Character(SearchableMixin, db.Model):
    # __searchable__ = ["movie_title","actor_name","character_name", "movie_year"]
    __searchable__ = {
        "movie_id": {"type": "keyword"},
        "actor_id": {"type": "keyword"},
        "movie_title": {
            "type": "text",
            "fields": {
                "raw": { 
                    "type":  "keyword"
                }
            }},
        "movie_year": {"type": "keyword"},
        "actor_name": {
            "type": "text",
            "fields": {
                "raw": { 
                    "type":  "keyword"
                }
            }},
        "character_name": {
            "type": "text",
            "fields": {
                "raw": { 
                    "type":  "keyword"
                }
            }},
        "order": {"type": "integer"}
    }
    __default_sort__ = ("character_name.raw", "asc")
    __sortable__ = [k for k, v in __searchable__.items() if v.get("type") == "keyword"] + [k + ".raw" for k, v in __searchable__.items() if v.get("fields")]
    __formfields__ = ["name"]
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

    # read only fields, need to be updated when link changes
    movie_title = db.Column(db.String(128))  # movie.title
    movie_year = db.Column(db.Integer)  # movie.year
    actor_name = db.Column(db.String(128))  # actor.name

    def __repr__(self):
        return "<Character {}, Actor {}, Movie {}, Order {}>".format(
            self.character_name, self.actor_name, self.movie_title, self.order
        )

    def to_dict(self):
        return {
            "id": self.id,
            "order": self.order,
            "actor_id": self.actor_id,
            "actor_image": self.actor.image_url
            if self.actor.image_url
            else self.actor._image_url_fallback,
            "actor_name": self.actor_name,
            "movie_id": self.movie_id,
            "movie_title": self.movie_title,
            "movie_year": self.movie.year,
            "movie_image": self.movie.poster_url,
            "character_name": self.character_name,
            "character_url": self.character_url,
        }


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
