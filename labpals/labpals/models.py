from labpals import app
from hashlib import md5
from labpals import login, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from labpals.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression):
        ids, total = query_index(cls.__tablename__, expression)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(SearchableMixin, UserMixin, db.Model):
    # Making able to search user's username by search bar
    __searchable__ = ['username']
    # Defining
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Linking user to corresponding group
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    # Making results from a user easily accessible by a SQLalchemy query
    results = db.relationship('Result', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in app.config['LABPALS_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Result(db.Model):
    # Defining data attributes for the results class
    # File content indexed as it is predicted most common search
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    filetype = db.Column(db.String(45))
    content = db.Column(db.String(255), index=True)
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)
    date_modif = db.Column(db.DateTime, default=datetime.utcnow)
    # Linking results class to IDs of groups and users
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Printing out the file type and date uploaded (used for python interpreter)
    def __repr__(self):
        return '<File Type {}>'.format(self.filetype)
        return '<Date Uploaded {}>'.format(self.date_upload)


class Group(SearchableMixin, db.Model):
    # Defining data attributes for group class
    # Groupname indexed as it is predicted most common search
    __searchable__ = ['groupname', 'location']
    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(255), index=True, unique=True)
    center = db.Column(db.String(255))
    location = db.Column(db.String(255))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    users = db.relationship('User', backref='useraffil', lazy='dynamic')
    results = db.relationship('Result', backref='group', lazy='dynamic')
    researchfields = db.relationship('ResearchField', backref='group', lazy='dynamic')

    # Printing out the name and location of the group (used for python interpreter)
    def __repr__(self):
        return '{}'.format(self.groupname)
        return '<Location {}>'.format(self.location)
        return '{}'.format(self.groupname)


class ResearchField(SearchableMixin, db.Model):
    # Defining data attributes for field class
    # Field indexed as it is predicted most common search
    __searchable__ = ['researchfield']
    id = db.Column(db.Integer, primary_key=True)
    researchfield = db.Column(db.String(255), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    # Printing out the research field (used for python interpreter)
    def __repr__(self):
        return '<Research field {}>'.format(self.researchfield)



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.UPLOAD],
            'Administrator': [Permission.UPLOAD, Permission.DELETE, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm


class Permission:
    UPLOAD = 1
    DELETE = 2
    ADMIN = 4
