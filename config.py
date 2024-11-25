import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Enable CSRF protection
WTF_CSRF_ENABLED = True
SECRET_KEY = 'secret-key-212312312'

