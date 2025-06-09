from app import db
from datetime import datetime
from flask_login import UserMixin
import secrets

# Association table for User <-> Inventory following relationship
inventory_followers = db.Table(
    'inventory_followers',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventories.id', ondelete='CASCADE'), primary_key=True),
    db.Column('followed_at', db.DateTime, default=datetime.utcnow)
)

# Users Table
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    followed_inventories = db.relationship(
        'Inventory',
        secondary=inventory_followers,
        back_populates='followers',
        lazy='dynamic'
    )


# Inventories Table
class Inventory(db.Model):
    __tablename__ = 'inventories'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_private = db.Column(db.Boolean, default=False, nullable=False)
    allowed_email_domain = db.Column(db.String(100), nullable=True)
    access_link_token = db.Column(db.String(64), nullable=True, unique=True)

    followers = db.relationship(
        'User',
        secondary=inventory_followers,
        back_populates='followed_inventories',
        lazy='dynamic'
    )

    def generate_access_link_token(self):
        self.access_link_token = secrets.token_urlsafe(32)

    def can_user_access(self, user, token=None):
        if not self.is_private:
            return True
        # Email domain check
        if self.allowed_email_domain and user.email.endswith(f"@{self.allowed_email_domain}"):
            return True
        # Access link token check
        if token and token == self.access_link_token:
            return True
        return False


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