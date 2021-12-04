from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from models import User

class UserAddForm(FlaskForm):
    """"Form for adding new user"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    
class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    
    
    