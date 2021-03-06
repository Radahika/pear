from app import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import sys
import pdb

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
    phone_number = db.Column(db.String(10))
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))
    chores = db.relationship('Chore', backref='author', lazy='dynamic')
    messages = db.relationship('Message', backref='Message.sender_id', primaryjoin='User.id==Message.receiver_id', lazy='dynamic')


    def sorted_messages(self):
        return self.messages.order_by(Message.timestamp.desc())

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

    def uncompleted_chore_count(self):
        chores = self.chores.all()
        count = 0
        for chore in chores:
            if not chore.status:
                count += 1
        return count

    def completed_chore_count(self):
        return self.chore_count() - self.uncompleted_chore_count()

    def get_plural_chore(self, count):
        if len(count) == 1:
            return "chore"
        return "chores"

    def message_count(self):
        return len(self.messages.all())

    def house_message_count(self):
        count = 0
        for message in self.home.messages.all():
            if message.sender is not self:
                count += 1
        return count

    def house_messages(self):
        return self.home.sorted_messages()

    def house_chores(self):
        return self.home.sorted_chores()

    def sorted_chores(self):
        return self.chores.order_by(Chore.timestamp.desc())

    def get_chores(self):
        tasks = []
        for chore in self.sorted_chores():
            tasks.append({'title': str(chore.title), 'description': str(chore.description), 'done': chore.status, 'timestamp': chore.timestamp})
        return tasks

    def get_chore(self, chore):
        task = []
        task.append({'id': chore.id, 'title': str(chore.title), 'description': str(chore.description), 'done': chore.get_status(), 'timestamp': chore.timestamp})
        return task

    def chore_size(self, chore):
        return len(chore.description)

    def unread_messages(self):
        unread = 0
        for m in self.messages:
            if not m.read:
                unread += 1
        return unread

    def __repr__(self):
        return '<User %r>' % (self.username)

class Chore(db.Model):
    __tablename__ = 'chore'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(140))
    status = db.Column(db.Boolean, default=False) #Initalize all chores as incompleted
    timestamp = db.Column(db.DateTime)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3

    def get_status(self):
        if self.status:
            return 'Done'
        return 'In Progress'

    def __repr__(self):
        return '<Chore %r, Complete: %r>' % (self.title, self.get_status())

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
    read = db.Column(db.Boolean, default=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    sender = db.relationship('User', foreign_keys='Message.sender_id')
    receiver = db.relationship('User', foreign_keys='Message.receiver_id')




    def pretty_time(self):
        return str(self.timestamp)[0:-10]

    def __repr__(self):
        return '<Message %r, Date: %r>' % (self.message, self.pretty_time())

