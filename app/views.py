from flask import render_template, flash, redirect
from app import app, db
#from .forms import 
#from app.models import 
from datetime import datetime


# index page for website
@app.route('/', methods=['GET', 'POST'])
def home():
    home = {
        'description': '''Welcome to this application.
                          '''
    }

    user_logged_in = False
    return render_template("home.html", title='Home', user_logged_in=user_logged_in, home=home)