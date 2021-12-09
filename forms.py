from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, Length
from wtforms.widgets.core import SubmitInput
from models import User

class UserAddForm(FlaskForm):
    """"Form for adding new user"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 25)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    
class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Keep me logged in')
    # submit = SubmitField('Log in')
    
    
class UserEditForm(FlaskForm):
    """User edit form"""
    
    email = StringField("Email", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(6, 20)])
    # submit = SubmitField("Submit")