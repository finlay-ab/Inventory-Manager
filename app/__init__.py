from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')  # Loads configuration from config.py

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app import views, models
