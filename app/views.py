from flask import render_template, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required
from app import app, db
from app.models import User
from app.forms import LoginForm, SignupForm
from werkzeug.security import generate_password_hash, check_password_hash

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
    flash('This is a test flash message!')
    user_logged_in = False
    return render_template("home.html", title='Home', user_logged_in=user_logged_in, cards=cards)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    flash('Start')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        flash('2')
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('3')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    flash('4')
    return render_template('authentication/login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    flash('This is a test flash message!')
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!')
        return redirect(url_for('login'))
    return render_template('authentication/signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))