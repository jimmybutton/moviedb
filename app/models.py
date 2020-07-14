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


def get_columns(columndef: list, fields: dict):
    columns = [dict(c, **{"title": fields[c.get("field")]["label"]}) for c in columndef]
    pre = [
        {"title": "", "field": "state", "checkbox": True},
        {"title": "", "field": "fav", "formatter": "favFormatter", "align": "center",},
    ]
    post = [
        {
            "title": "Last modified",
            "field": "modified_timestamp",
            "formatter": "lastModFormatter",
        },
    ]
    return pre + columns + post


def get_search_fields(fields):
    searchable = {
        "id": {"type": "keyword"},
        "modified_timestamp": {"type": "date"},
    }
    for name, definition in fields.items():
        ftype = definition.get("type")
        if ftype == "string":
            searchable[name] = {
                "type": "text",
                "fields": {"raw": {"type": "keyword"}},
            }
        elif ftype == "text":
            searchable[name] = {"type": "text"}
        elif ftype == "discrete":
            searchable[name] = {"type": "keyword"}
        elif ftype == "integer":
            searchable[name] = {"type": "integer"}
        elif ftype == "float":
            searchable[name] = {"type": "float"}
        elif ftype in ["date", "datetime"]:
            searchable[name] = {"type": "date"}
    return searchable


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
    __fields__ = {
        "title": {
            "label": "Title",
            "type": "string",
            "column": {"order": 1, "formatter": "titleFormatter"},
        },
        "year": {"label": "Year", "type": "integer", "column": {"order": 2}},
        "director": {"label": "Director", "type": "string", "column": {"order": 3}},
        "category": {
            "label": "Category",
            "type": "discrete",
            "column": {"order": 4},
            "options": [
                "Action",
                "Adventure",
                "Animation",
                "Biography",
                "Comedy",
                "Crime",
                "Drama",
                "Film-Noir",
                "Horror",
                "Mystery",
                "Western",
            ],
        },
        "certificate": {
            "label": "Certificate",
            "type": "discrete",
            "column": {"order": 4, "visible": False},
            "options": [
                "U",
                "12",
                "12A",
                "15",
                "18",
                "R18",
                "A",
                "PG",
                "U/A",
                "S",
                "X",
            ],
        },
        "release_date": {"label": "Release date", "type": "string"},
        "plot_summary": {"label": "Plot summary", "type": "text"},
        "rating_value": {"label": "Rating", "type": "float", "column": {"order": 5}},
        "rating_count": {"label": "Rating count", "type": "integer"},
        "poster_url": {"label": "Poster", "type": "image_url"},
        "runtime": {
            "label": "Runtime (min)",
            "type": "integer",
            "column": {"order": 6, "visible": False},
        },
        "url": {"label": "Url (imdb)", "type": "url"},
    }
    __searchable__ = get_search_fields(__fields__)
    __formfields__ = list(__fields__.keys())
    __columndef__ = [
        {"field": "title", "formatter": "imageLinkFormatter"},
        {"field": "year"},
        {"field": "director"},
        {"field": "category"},
        {"field": "certificate", "visible": False},
        {"field": "rating_value"},
        {"field": "runtime", "visible": False},
    ]
    __columns__ = get_columns(__columndef__, __fields__)
    __default_sort__ = ("rating_value", "desc")

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

    @property
    def default_image_url(self):
        if self.poster_url:
            return self.poster_url
        else:
            return "https://m.media-amazon.com/images/G/01/imdb/images/nopicture/small/film-293970583._CB469775754_.png"

    def to_dict(self):
        fields = ["id", "modified_timestamp", "default_image_url"] + list(self.__fields__.keys())
        data = {}
        for f in fields:
            value = getattr(self, f)
            if isinstance(value, datetime.datetime):
                data[f] = value.isoformat()
            else:
                data[f] = value
        return data


class People(SearchableMixin, db.Model):
    __searchable__ = {
        "id": {"type": "keyword"},
        "modified_timestamp": {"type": "date"},
        "name": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "bio": {"type": "text"},
        "dob": {"type": "date"},
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
    __searchable__ = {
        "movie_id": {"type": "keyword"},
        "actor_id": {"type": "keyword"},
        "movie_title": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "movie_year": {"type": "keyword"},
        "actor_name": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "character_name": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "order": {"type": "integer"},
    }
    __default_sort__ = ("character_name.raw", "asc")
    __sortable__ = [
        k for k, v in __searchable__.items() if v.get("type") == "keyword"
    ] + [k + ".raw" for k, v in __searchable__.items() if v.get("fields")]
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
