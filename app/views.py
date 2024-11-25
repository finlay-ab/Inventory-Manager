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

    return render_template('home.html', title='Home', home=home)