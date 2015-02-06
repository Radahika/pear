import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['radhika.marvin@yahoo.com',
            'k3vinhwang@gmail.com']

MAX_SEARCH_RESULTS = 50
# pagination
MESSAGES_PER_PAGE = 4
CHORES_PER_PAGE = 5

TWILIO_ACCOUNT_SID = "AC9e6b192f2928c17fae15a8ccb16225fb"
TWILIO_AUTH_TOKEN = "d0917cd860e126817cfe12a8619cadc1"
TWILIO_NUMBER = "+17608204674"
