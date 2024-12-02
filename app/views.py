from flask import render_template, flash, redirect
from app import app, db
#from .forms import 
#from app.models import 
from datetime import datetime


# index page for website
@app.route('/', methods=['GET', 'POST'])
def home():
    cards = [
    {"title": "Browse All Inventories", "description": "Explore all available inventories created by users.", "link": "#"},
    {"title": "Browse Followed Inventories", "description": "View inventories you are following.", "link": "#"},
    {"title": "My Inventory", "description": "Manage your own inventory and items.", "link": "#"},
    {"title": "Manage My Loans", "description": "View your loans and the state of your requests.", "link": "#"},
    {"title": "TBD", "description": "not sure", "link": "#"},
    {"title": "Account Settings", "description": "Manage your settings.", "link": "#"}
    ]

    user_logged_in = False
    return render_template("home.html", title='Home', user_logged_in=user_logged_in, cards=cards)