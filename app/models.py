from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship("User", foreign_keys=[created_id])
    modified_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.relationship("User", foreign_keys=[modified_id])

    title = db.Column(db.String(128), index=True)
    year = db.Column(db.Integer)
    certificate = db.Column(db.String(16))
    category = db.Column(db.String(64))
    release_date = db.Column(db.String(128))
    plot_summary = db.Column(db.String(512))
    director = db.Column(db.String(64))
    rating_value = db.Column(db.Float)
    rating_count = db.Column(db.Integer)
    poster_url = db.Column(db.String(256))
    runtime = db.Column(db.String(16))
    url = db.Column(db.String(64))

    def __repr__(self):
        return "<Movie {}>".format(self.title)
    
    @property
    def displayname(self):
        return f"{self.title} ({self.year})"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))