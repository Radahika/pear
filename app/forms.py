from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextField, PasswordField
from wtforms.validators import DataRequired
from app.models import User

class resetForm(Form):
    email = StringField('email', validators=[DataRequired()])

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class CreateForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    house = StringField('house', validators=[DataRequired()])

class EditForm(Form):
    username = TextField('username', validators=[DataRequired()])

    def __init__(self, original_username, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_username = original_username

    def validate(self):
        if not Form.validate(self):
            return False
        if self.username.data == self.original_username:
            return True
        user = User.query.filter_by(username=self.username.data).first()
        if user != None:
            self.username.errors.append('This username is already in use. Please choose another one.')
            return False
        return True
