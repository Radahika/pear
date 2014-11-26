from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
#    house = db.relationship('House', backref='user', lazy='dynamic', uselist=False)
    house_id = db.Column(db.String(64), db.ForeignKey('house.id'))

    def __repr__(self):
        return '<User %r>' % (self.nickname)



class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    housename = db.Column(db.String(64), index=True, unique=True)
#    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    residents = db.relationship('User', backref='house', lazy='dynamic')

    def __repr__(self):
        return '<House %r>' % (self.housename)


