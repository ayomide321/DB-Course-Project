from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __table__ = db.Model.metadata.tables['user']
    def get_id(self):
           return (self.ID)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    print(id)
    return User.query.get(int(id))

class People(db.Model):
    __table__ = db.Model.metadata.tables['people']

    def getPlayerID(self):
        return (self.playerID)

    def __repr__(self):
        return '<People Information For {}>'.format(self.playerID)

class Batting(db.Model):
    __table__ = db.Model.metadata.tables['batting']

    def __repr__(self):
        return '<Batting Information For {}>'.format(self.playerID)

class Pitching(db.Model):
    __table__ = db.Model.metadata.tables['pitching']

    def __repr__(self):
        return '<pitching Information For {}>'.format(self.playerID)

class Fielding(db.Model):
    __table__ = db.Model.metadata.tables['fielding']

    def __repr__(self):
        return '<Fielding Information For {}>'.format(self.playerID)

class Team(db.Model):
    __table__ = db.Model.metadata.tables['team']

    def __repr__(self):
        return '<team Information For {}>'.format(self.teamID)

class AuditTrail(db.Model):
    __table__ = db.Model.metadata.tables['audit_trail']

    def __repr__(self):
        return '<Audit Information For {}>'.format(self.username)




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.username'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)