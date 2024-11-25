from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config')  # Loads configuration from config.py

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
