from app import db, login
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.search import (
    add_to_index,
    remove_from_index,
    query_index,
    query_index_full_text,
)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index_full_text(
            cls.__tablename__, expression, page, per_page
        )
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)),
            total,
        )

    @classmethod
    def search_by_fields(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
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
        for obj in cls.query:
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
    __searchable__ = ["title", "plot_summary"]
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
    created_timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    created_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_by = db.relationship("User", foreign_keys=[created_id])
    modified_timestamp = db.Column(
        db.DateTime, index=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
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

    def __repr__(self):
        return "<Movie {}>".format(self.title)

    @property
    def displayname(self):
        return f"{self.title} ({self.year})"

    def to_dict(self):
        fields = ['id', 'modified_timestamp'] + self.__formfields__
        data = {}
        for f in fields:
            data[f] = getattr(self, f)
        return data

class People(SearchableMixin, db.Model):
    __searchable__ = ["name", "birthname", "bio"]
    __formfields__ = ['name','url','image_url','dob','birthname','height','bio']
    id = db.Column(db.Integer, primary_key=True)
    created_timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    created_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_by = db.relationship("User", foreign_keys=[created_id])
    modified_timestamp = db.Column(
        db.DateTime, index=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
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

    def __repr__(self):
        return "<Person {}>".format(self.name)

    def to_dict(self):
        fields = ['id', 'modified_timestamp'] + self.__formfields__
        data = {}
        for f in fields:
            value = getattr(self, f)
            if type(value) is datetime.date:
                data[f] = value.strftime(r"%a, %d %b %Y")
            else:
                data[f] = value
        return data

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
