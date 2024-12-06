from flask import render_template, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from datetime import datetime
from app.models import User, Inventory, Item, Loan
from app.forms import LoginForm, SignupForm, CreateInventoryForm, CreateItemForm, DeleteItemButtonForm, LoanButtonForm, RejectButtonForm, ApproveButtonForm, EditItemButtonForm, ClearLoanButtonForm, CancelLoanButtonForm, ReturnLoanButtonForm
from werkzeug.security import generate_password_hash, check_password_hash

# index page for website
@app.route('/', methods=['GET', 'POST'])
def home():
    cards = [
        {"title": "Browse All Inventories", "description": "Explore all available inventories created by users.", "link": "/all-inventories"},
        {"title": "Browse Followed Inventories", "description": "View inventories you are following.", "link": "#"},
        {"title": "My Inventory", "description": "Manage your own inventory and items.", "link": "/my-inventory"},
        {"title": "Requested Loans", "description": "View your loan requests.", "link": "/view-loans"},
        {"title": "TBD", "description": "not sure", "link": "/manage-loans"},
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


@app.route('/all-inventories', methods=['GET', 'POST'])
def all_inventories():
    inventories = Inventory.query.all()
    cards = []
    
    for inventory in inventories:
        card = {
            "title": inventory.title,
            "description": inventory.description,
            "link": url_for('view_inventory', inventory_id=inventory.id)
        }

        cards.append(card)
    
    return render_template('inventory/all-inventories.html', cards=cards)

@app.route('/view-inventory/<int:inventory_id>', methods=['GET', 'POST'])
def view_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)

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
            loan_form = LoanButtonForm()
            card = {
                "name": item.name,
                "description": item.description,
                "repair_status": item.condition.title().replace("_", " "),
                "repair_status_class": repair_status_badge.get(item.condition),
                "loan_status": item.loan_status.title().replace("_", " "),  
                "loan_status_class": loan_status_badge.get(item.loan_status), 
                "loan_form": loan_form,
                "loan_link":  url_for('loan_request', item_id=item.id), 
            }
            cards.append(card)                    

        return render_template('inventory/view-inventory.html', cards=cards, inventory=inventory)
    else:
        flash("Error: could not find inventory", "warning")
        return redirect(url_for('all_inventories'))
    
@app.route('/loan-request/<int:item_id>', methods=['GET', 'POST'])
@login_required
def loan_request(item_id):

    item = Item.query.get_or_404(item_id)
    if not item:
        flash('item not found.', 'error')
        return redirect(url_for('all_inventories')) 
    
    if item.loan_status != 'available':
        flash('item not avaliable for loan.', 'error')
        return redirect(url_for('view_inventory', inventory_id=item.inventory_id)) 
    
    user_id = Inventory.query.filter_by(id=item.inventory_id).first().owner_id
    
    loan = Loan(
        item_id=item_id,
        borrower_id=current_user.id,
        owner_id=user_id,
        status='pending',
        request_date=datetime.utcnow()
    )

    db.session.add(loan)
    db.session.commit()

    flash('Loan request submitted successfully.', 'success')
    return redirect(url_for('view_inventory', inventory_id=item.inventory_id))


@app.route('/manage-loans', methods=['GET', 'POST'])
@login_required
def manage_loans():
    
    loan_status_badge = {
        "pending": "warning",
        "approved": "success",
        "rejected": "danger",
        "returned": "info",
    }


    loans = Loan.query.filter_by(owner_id=current_user.id).all()

    if len(loans) == 0:
        flash("you have no loan requests right right now!")
    
    
    cards = []
    reject_form = RejectButtonForm()
    approve_form = ApproveButtonForm()

    for loan in loans:
        item = Item.query.get(loan.item_id)

        if item:
            inventory = Inventory.query.get(item.inventory_id)
            card = {
                "item_name": item.name,
                "item_description": item.description,
                "inventory_name": inventory.title,
                "request_status": item.loan_status,
                "request_date": loan.request_date,
                "approve_form": approve_form,
                "approve_link": url_for('approve_loan', loan_id=loan.id),
                "reject_form": reject_form,
                "reject_link": url_for('reject_loan', loan_id=loan.id),
                "loan_status_class": loan_status_badge.get(loan.status),
                "loan_status" : loan.status
            }

            cards.append(card)
    
    return render_template('loans/manage-loans.html', cards=cards)



@app.route('/view-loans', methods=['GET', 'POST'])
@login_required
def view_loan_requests():

    loan_status_badge = {
        "pending": "warning",
        "approved": "success",
        "rejected": "danger",
        "returned": "info",
    }


    loans = Loan.query.filter_by(borrower_id=current_user.id).all()

    if len(loans) == 0:
        flash("you have no loans right now!")
    
    
    cards = []

    for loan in loans:
        link = None
        loan_form = None
        if (loan.status == 'pending'):
            link = url_for('cancel_loan_request', loan_id=loan.id)
            loan_form = CancelLoanButtonForm()
        elif (loan.status == 'approved'):
            link = url_for('return_loan_request', loan_id=loan.id)
            loan_form = ReturnLoanButtonForm()
        else:
            link = url_for('clear_loan_request', loan_id=loan.id)
            loan_form = ClearLoanButtonForm()

        item = Item.query.get(loan.item_id)

        if item:
            inventory = Inventory.query.get(item.inventory_id)
            card = {
                "item_name": item.name,
                "item_description": item.description,
                "inventory_name": inventory.title,
                "request_status": item.loan_status,
                "request_date": loan.request_date,
                "loan_form": loan_form,
                "link": link,
                "loan_status_class": loan_status_badge.get(loan.status),
                "loan_status" : loan.status
            }

            cards.append(card)
    
    return render_template('loans/view-loans.html', cards=cards)

@app.route('/cancel-loan-request/<int:loan_id>', methods=['POST'])
@login_required
def cancel_loan_request(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.borrower_id != current_user.id and loan.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('view_loan_requests'))

    db.session.delete(loan)
    db.session.commit()
    flash('Loan deleted', 'success')
    return redirect(url_for('view_loan_requests'))

@app.route('/clear-loan-request/<int:loan_id>', methods=['POST'])
@login_required
def clear_loan_request(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.borrower_id != current_user.id and loan.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('view_loan_requests'))

    db.session.delete(loan)
    db.session.commit()
    flash('Loan Cleared', 'success')
    return redirect(url_for('view_loan_requests'))

@app.route('/return-loan-request/<int:loan_id>', methods=['POST'])
@login_required
def return_loan_request(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    item = Item.query.get_or_404(loan.item_id)
    
    if loan.borrower_id != current_user.id and loan.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('view_loan_requests'))
    
    item.loan_status = 'available'

    db.session.delete(loan)
    db.session.commit()
    flash('Loan Return', 'success')
    return redirect(url_for('view_loan_requests'))

@app.route('/approve-loan-request/<int:loan_id>', methods=['POST'])
@login_required
def approve_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    item = Item.query.get_or_404(loan.item_id)
    
    if  loan.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('manage_loans'))
    
    item.loan_status = 'on_loan'
    loan.status = 'approved'

    db.session.commit()

    flash('Loan approved', 'success')
    return redirect(url_for('manage_loans'))

@app.route('/reject-loan-request/<int:loan_id>', methods=['POST'])
@login_required
def reject_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if  loan.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('manage_loans'))

    loan.status = 'rejected'

    db.session.commit()
    flash('Loan rejected', 'success')
    return redirect(url_for('manage_loans'))

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
