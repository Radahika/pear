from app import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import sys

if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask.ext.whooshalchemy as whooshalchemy

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class House(db.Model):
    __searchable__ = ['housename']
    __tablename__ = 'house'
    id = db.Column(db.Integer, primary_key=True)
    housename = db.Column(db.String(64), index=True, unique=True)
    users = db.relationship('User', backref='home', lazy='dynamic')

    def __repr__(self):
        return '<House %r>' % (self.housename)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))
    chores = db.relationship('Chore', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3

    @staticmethod
    def make_unique_username(username):
        if User.query.filter_by(username=username).first() is None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if User.query.filter_by(username=new_username).first() is None:
                break
            version += 1
        return new_username

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count()

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return '<User %r>' % (self.username)

class Chore(db.Model):
    __tablename__ = 'chore'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(140))
    status = db.Column(db.Boolean, default=False) #Initalize all chores as incompleted
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3


    def __repr__(self):
        return '<Chore %r, Complete: %r>' % (self.title, self.status)


#class House(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #housename = db.Column(db.String(64), index=True, unique=True)
    #users = db.relationship('User', backref='home', lazy='dynamic')

    #def __repr__(self):
        #return '<House %r>' % (self.housename)

#class User(db.Model):
    #id = db.Column(db.Integer, primary_key = True)
    #username = db.Column(db.String(64), index=True, unique=True)
    #house_id = db.Column(db.Integer, db.ForeignKey('house.id'))

    #def __repr__(self):
        #return '<User %r>' % (self.username)

if enable_search:
    whooshalchemy.whoosh_index(app, House)
