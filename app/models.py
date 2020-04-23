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
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # created_by = db.relationship("User", backref="movies_created", lazy="dynamic")
    title = db.Column(db.String(64), index=True)
    description = db.Column(db.String(200))
    year = db.Column(db.Integer)
    stars = db.Column(db.Float)

    def __repr__(self):
        return "<Movie {}>".format(self.title)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))