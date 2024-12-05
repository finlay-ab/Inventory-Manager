from flask import render_template, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from app.models import User, Inventory, Item
from app.forms import LoginForm, SignupForm, CreateInventoryForm, CreateItemForm, DeleteItemButtonForm, EditItemButtonForm
from werkzeug.security import generate_password_hash, check_password_hash


# index page for website
@app.route('/', methods=['GET', 'POST'])
def home():
    cards = [
        {"title": "Browse All Inventories", "description": "Explore all available inventories created by users.", "link": "#"},
        {"title": "Browse Followed Inventories", "description": "View inventories you are following.", "link": "#"},
        {"title": "My Inventory", "description": "Manage your own inventory and items.", "link": "/my-inventory"},
        {"title": "Manage My Loans", "description": "View your loans and the state of your requests.", "link": "#"},
        {"title": "TBD", "description": "not sure", "link": "#"},
        {"title": "Account Settings", "description": "Manage your settings.", "link": "#"}
    ]

    return render_template("home.html", title='Home', user_logged_in=current_user.is_authenticated, cards=cards)


@app.route('/my-inventory')
@login_required
def my_inventory():
    inventory = Inventory.query.filter_by(owner_id=current_user.id).first()

    repair_status_badge = {
        "functional": "success",
        "minor_repair": "warning",
        "under_repair": "info",
        "out_of_service": "danger",
        "missing_parts": "secondary",
        "inspection_needed": "primary",
    }

    loan_status_badge = {
        "available": "success",
        "on_loan": "warning",
        "unavailable": "secondary",
    }

    if inventory:
        items = Item.query.filter_by(inventory_id=inventory.id).all()
        cards = []
        for item in items:
            edit_form = EditItemButtonForm()
            delete_form = DeleteItemButtonForm()
            card = {
                "name": item.name,
                "description": item.description,
                "repair_status": item.condition.title().replace("_", " "),
                "repair_status_class": repair_status_badge.get(item.condition),
                "loan_status": item.loan_status.title().replace("_", " "),  
                "loan_status_class": loan_status_badge.get(item.loan_status), 
                "edit_form": edit_form,
                "edit_link":  url_for('edit_item', item_id=item.id), 
                "delete_form": delete_form, 
                "delete_link": url_for('delete_item', item_id=item.id), 
            }
            cards.append(card)

        return render_template('inventory/my-inventory.html', cards=cards, inventory=inventory)
    else:
        return redirect(url_for('create_inventory'))


@app.route('/create-inventory', methods=['GET', 'POST'])
@login_required
def create_inventory():
    form = CreateInventoryForm()
    if form.validate_on_submit():
        new_inventory = Inventory(owner_id=current_user.id, title=form.title.data, description=form.description.data)
        db.session.add(new_inventory)
        db.session.commit()
        return redirect(url_for('my_inventory'))
    return render_template('inventory/create-inventory.html', form=form)


@app.route('/create-item', methods=['GET', 'POST'])
def create_item():
    inventory = Inventory.query.filter_by(owner_id=current_user.id).first()

    if not inventory:
        flash("Inventory not found.", "danger")
        return redirect(url_for('my_inventory'))

    form = CreateItemForm()
    if form.validate_on_submit():
        new_item = Item(
            inventory_id=inventory.id,
            name=form.name.data,
            description=form.description.data,
            loan_status=form.loan_status.data,
            condition=form.condition.data
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Item created successfully!', 'success')
        return redirect(url_for('my_inventory'))
    return render_template('item/create-item.html', form=form, inventory_id=inventory.id)

@app.route('/edit/<int:item_id>',  methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    inventory = Inventory.query.filter_by(id=item.inventory_id).first()
    user = User.query.filter_by(id=item.inventory_id).first()

    if inventory.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('my_inventory'))
    
    form = CreateItemForm(obj=item)
    if form.validate_on_submit():
        item.name=form.name.data
        item.description=form.description.data
        item.loan_status=form.loan_status.data
        item.condition=form.condition.data
        
        db.session.commit()
        flash('Item edited successfully!', 'success')
        return redirect(url_for('my_inventory'))
    return render_template('item/edit-item.html', form=form, item=item)

    
@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    inventory = Inventory.query.filter_by(id=item.inventory_id).first()
    user = User.query.filter_by(id=item.inventory_id).first()

    if inventory.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('my_inventory'))

    db.session.delete(item)
    db.session.commit()
    flash('Item deleted', 'success')
    return redirect(url_for('my_inventory'))


@app.route('/manage-inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    inventory = Inventory.query.filter_by(owner_id=current_user.id).first()

    if not inventory:
        flash("Inventory not found.", "danger")
        return redirect(url_for('my_inventory'))

    form = CreateInventoryForm(obj=inventory)

    if form.validate_on_submit():
        inventory.title = form.title.data
        inventory.description = form.description.data
        db.session.commit()
        flash("Inventory updated successfully!", "success")
        return redirect(url_for('my_inventory'))

    return render_template("inventory/manage-inventory.html", form=form, inventory=inventory)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    return render_template('authentication/login.html', title='Home', user_logged_in=current_user.is_authenticated, form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('authentication/signup.html',title='Home', user_logged_in=current_user.is_authenticated, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
