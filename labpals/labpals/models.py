from hashlib import md5
from labpals import login, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    #Defining
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    #Linking user to corresponding group
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Result(db.Model):
    #Defining data attributes for the results class
    #File content indexed as it is predicted most common search
    id = db.Column(db.Integer, primary_key=True)
    filetype = db.Column(db.String(45))
    content = db.Column(db.String(255), index=True)
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)
    date_modif = db.Column(db.DateTime, default=datetime.utcnow)
    # Linking results class to IDs of groups and users
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #Printing out the file type and date uploaded (used for python interpreter)
    def __repr__(self):
        return '<File Type {}>'.format(self.filetype)
        return '<Date Uploaded {}>'.format(self.date_upload)



class Group(db.Model):
    #Defining data attributes for group class
    #Groupname indexed as it is prediceted most common search
    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(255), index=True)
    location = db.Column(db.String(255))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #Printing out the name and location of the group (used for python interpreter)
    def __repr__(self):
        return '<User {}>'.format(self.groupname)
        return '<Location {}>'.format(self.location)
