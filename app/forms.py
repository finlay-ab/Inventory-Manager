from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField, BooleanField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')

class CreateInventoryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create')

class CreateItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    loan_status = SelectField(
        'Loan Status',
        choices=[
            ('available', 'Available'),
            ('on_loan', 'On Loan'),
            ('unavailable', 'Unavailable')
        ],
        validators=[DataRequired()]
    )
    condition = SelectField(
        'Condition',
        choices=[
            ('functional', 'Functional'),
            ('minor_repair', 'Minor Repair'),
            ('under_repair', 'Under Repair'),
            ('out_of_service', 'Out of Service'),
            ('missing_parts', 'Missing Parts'),
            ('inspection_needed', 'Inspection Needed')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Create Item')

    
class DeleteItemButtonForm(FlaskForm):
    submit = SubmitField('Delete')

class EditItemButtonForm(FlaskForm):
    submit = SubmitField('Edit')