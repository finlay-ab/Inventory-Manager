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

    # rendered on home page as a card
    # must have a title, description and link
    cards = [
        {"title": "Browse All Inventories", "description": "Explore all available inventories created by users.", "link": "/all-inventories"},
        {"title": "My Inventory", "description": "Manage your own inventory and items.", "link": "/my-inventory"},
        {"title": "Manage Loans", "description": "manage loan requests to your own inventory", "link": "/manage-loans"},
    ]

    return render_template("home.html", title='Home', user_logged_in=current_user.is_authenticated, cards=cards)

# view current users inventory
@app.route('/my-inventory')
@login_required
def my_inventory():
    
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

    #get current users inventory 
    inventory = Inventory.query.filter_by(owner_id=current_user.id).first()

    # if inventory exists then
    if inventory:
        # get all the items in that inventory
        items = Item.query.filter_by(inventory_id=inventory.id).all()

        # initilise empty list of cards
        cards = []

        # foreach item in the inventory
        for item in items:
            #set forms
            edit_form = EditItemButtonForm()
            delete_form = DeleteItemButtonForm()

            #make a card that can be displayed 
            card = {
                "name": item.name,
                "description": item.description,
                # must make _ a space
                "repair_status": item.condition.title().replace("_", " "),
                "loan_status": item.loan_status.title().replace("_", " "),  
                "repair_status_class": repair_status_badge.get(item.condition),
                "loan_status_class": loan_status_badge.get(item.loan_status), 
                # forms and links for the buttons and wtforms
                "edit_form": edit_form,
                "edit_link":  url_for('edit_item', item_id=item.id), 
                "delete_form": delete_form, 
                "delete_link": url_for('delete_item', item_id=item.id), 
            }

            # adds card to list of cards 
            cards.append(card)

        return render_template('inventory/my-inventory.html', cards=cards, inventory=inventory, user_logged_in=current_user.is_authenticated)
    
    # if the user has no inventory direct them to make one
    else:
        return redirect(url_for('create_inventory'))


# allow the user to create an inventory
@app.route('/create-inventory', methods=['GET', 'POST'])
@login_required
def create_inventory():
    # initilises create inventory form 
    form = CreateInventoryForm()

    # if a valid form is submitted 
    if form.validate_on_submit():
        # create inventory 
        new_inventory = Inventory(owner_id=current_user.id, title=form.title.data, description=form.description.data)
        #update database
        db.session.add(new_inventory)
        db.session.commit()
        # redirect user to there new inventory
        return redirect(url_for('my_inventory'))
    
    return render_template('inventory/create-inventory.html', form=form, user_logged_in=current_user.is_authenticated)

# allow the user to craete an item for there inventory
@app.route('/create-item', methods=['GET', 'POST'])
def create_item():
    inventory = Inventory.query.filter_by(owner_id=current_user.id).first()

    # if the current user doesnt have an inventory redirect them to make one
    if not inventory:
        flash("Inventory not found.", "danger")
        return redirect(url_for('my_inventory'))

    # initilise form
    form = CreateItemForm()

    # if valid form is submitted
    if form.validate_on_submit():
        
        # create a new item with the form data
        new_item = Item(
            inventory_id=inventory.id,
            name=form.name.data,
            description=form.description.data,
            loan_status=form.loan_status.data,
            condition=form.condition.data
        )
        # add and save item to the database
        db.session.add(new_item)
        db.session.commit()
        flash('Item created successfully!', 'success')
        # return the user to there inventory
        return redirect(url_for('my_inventory'))
    
    return render_template('item/create-item.html', form=form, inventory_id=inventory.id, user_logged_in=current_user.is_authenticated)

# allows the user to edit a given item (must own item to edit it)
@app.route('/edit/<int:item_id>',  methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    # get item
    item = Item.query.get_or_404(item_id)

    # get the user who owns the item 
    inventory = Inventory.query.filter_by(id=item.inventory_id).first()    
    user = User.query.filter_by(id=item.inventory_id).first()

    # if the user doesnt own the current item 
    if inventory.owner_id != current_user.id:
        # give error + redirect back there inventory
        flash("Error cant edit item that you dont own!")
        return redirect(url_for('my_inventory'))
    
    # initlise item form with selected items information 
    form = CreateItemForm(obj=item)
    if form.validate_on_submit():
        #update item infomation 
        item.name=form.name.data
        item.description=form.description.data
        item.loan_status=form.loan_status.data
        item.condition=form.condition.data
        
        #save to db and output success
        db.session.commit()
        flash('Item edited successfully!', 'success')
        #return user to there inventory
        return redirect(url_for('my_inventory'))
    return render_template('item/edit-item.html', form=form, item=item, user_logged_in=current_user.is_authenticated)

# non visable route to delete items   
@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):

    # get selected item 
    item = Item.query.get_or_404(item_id)

    # get the user who owns the item 
    inventory = Inventory.query.filter_by(id=item.inventory_id).first()
    user = User.query.filter_by(id=item.inventory_id).first()

    # if the user doesnt own the current item output error and redirect
    if inventory.owner_id != current_user.id:
        flash("Error")
        return redirect(url_for('my_inventory'))

    # delete item and update db
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted', 'success')
    return redirect(url_for('my_inventory'))

# lets the user rename and change the inventory description
@app.route('/manage-inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    inventory = Inventory.query.filter_by(owner_id=current_user.id).first()

    # if the user doesnt have an inventory warn them and direct them to make one
    if not inventory:
        flash("Inventory not found.", "danger")
        return redirect(url_for('my_inventory'))

    # initilise form and give it exisiting inventory data 
    form = CreateInventoryForm(obj=inventory)

    # if a valid form is submitted then
    if form.validate_on_submit():
        # update data 
        inventory.title = form.title.data
        inventory.description = form.description.data

        #update db with new data
        db.session.commit()
        flash("Inventory updated successfully!", "success")
        return redirect(url_for('my_inventory'))

    return render_template("inventory/manage-inventory.html", form=form, inventory=inventory, user_logged_in=current_user.is_authenticated)

# dispaly all existing inventories
@app.route('/all-inventories', methods=['GET', 'POST'])
def all_inventories():

    #get all inventoreis 
    inventories = Inventory.query.all()
    cards = []
    
    for inventory in inventories:
        # make card of each inventory
        card = {
            "title": inventory.title,
            "description": inventory.description,
            "link": url_for('view_inventory', inventory_id=inventory.id)
        }

        cards.append(card)
    
    # display cards
    return render_template('inventory/all-inventories.html', cards=cards, user_logged_in=current_user.is_authenticated)


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
        "requested": "warning",
        "unavailable": "secondary",
    }

    if not current_user.is_authenticated:
        flash("you must be signed in to loan items")

    if inventory:
        items = Item.query.filter_by(inventory_id=inventory.id).all()
        cards = []
        for item in items:

            item_loan_status = item.loan_status
            can_loan = "False"
            if current_user.is_authenticated:
                if item.loan_status == 'available':
                    current_user_loans = Loan.query.filter_by(borrower_id=current_user.id, item_id=item.id).first()
                    if current_user_loans:
                        item_loan_status = 'requested'
                    else:
                        can_loan = "True"

            

            loan_form = LoanButtonForm()
            card = {
                "name": item.name,
                "description": item.description,
                "repair_status": item.condition.title().replace("_", " "),
                "repair_status_class": repair_status_badge.get(item.condition),
                "loan_status": item_loan_status.title().replace("_", " "),  
                "loan_status_class": loan_status_badge.get(item_loan_status), 
                "loan_form": loan_form,
                "loan_link":  url_for('loan_request', item_id=item.id), 
                "can_loan": can_loan
            }
            cards.append(card)                    

        return render_template('inventory/view-inventory.html', cards=cards, inventory=inventory, user_logged_in=current_user.is_authenticated)
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
            borrower_name = User.query.get_or_404(loan.borrower_id).username
            card = {
                "item_name": item.name,
                "item_description": item.description,
                "borrower_name": borrower_name,
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
    
    return render_template('loans/manage-loans.html', cards=cards, user_logged_in=current_user.is_authenticated)



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
    
    return render_template('loans/view-loans.html', cards=cards, user_logged_in=current_user.is_authenticated)


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
