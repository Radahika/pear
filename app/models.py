from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    house = db.relationship('House', uselist=False, backref='user',)

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

    def __repr__(self):
        return '<User %r>' % (self.username)

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    housename = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<House %r>' % (self.housename)


