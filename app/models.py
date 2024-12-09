from app import db
from datetime import datetime
from flask_login import UserMixin

#added cascade with help from 
#https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete
# (casecade in this case means if the user is deleted all the data assosiated with there id is removed)

# Users Table
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
# Inventories Table
class Inventory(db.Model):
    __tablename__ = 'inventories'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Items Table
class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    loan_status = db.Column(
        db.Enum(
            'available',
            'on_loan',
            'unavailable',
            name='loan_status_enum',
        ),
        nullable=False,
        default='unavailable'
    )
    condition = db.Column(
        db.Enum(
            'functional',
            'minor_repair',
            'under_repair',
            'out_of_service',
            'missing_parts',
            'inspection_needed',
            name='condition_enum',
        ),
        nullable=False,
        default='functional'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Loans Table
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    owner_id = db.Column(db.Integer, nullable=True) 
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'returned', name='loan_status'), default='pending')
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

# un used, was planned but not implimented!
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)