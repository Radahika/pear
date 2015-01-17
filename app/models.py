from app import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import sys
import pdb

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class House(db.Model):
    __tablename__ = 'house'
    id = db.Column(db.Integer, primary_key=True)
    housename = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    users = db.relationship('User', backref='home', lazy='dynamic')
    chores = db.relationship('Chore', backref='home', lazy='dynamic')
    events = db.relationship('Event', backref='home', lazy='dynamic')
    messages = db.relationship('Message', backref='home', lazy='dynamic')

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def message_count(self):
        return len(self.messages)

    def sorted_messages(self):
        return self.messages.order_by(Message.timestamp.desc())

    def sorted_chores(self):
        return self.chores.order_by(Chore.timestamp.desc())

    def __repr__(self):
        return '<House %r>' % (self.housename)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))
    chores = db.relationship('Chore', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    messages = db.relationship('Message', backref='author', lazy='dynamic')

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

    def invalidate_auth_token(self):
        self.token = None

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

    def get_housename(self):
        return str(self.home.housename)

    def chore_count(self):
        return len(self.chores.all())

    def message_count(self):
        return len(self.messages.all())

    def house_messages(self):
        return self.home.sorted_messages()

    def house_chores(self):
        return self.home.sorted_chores()

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
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3


    def __repr__(self):
        return '<Chore %r, Complete: %r>' % (self.title, self.status)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    description = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))

    def __repr__(self):
        return '<Event %r, Date: %r>' % (self.title, self.timestamp)

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), index=True)
    timestamp = db.Column(db.DateTime)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Message %r, Date: %r>' % (self.message, self.timestamp)

