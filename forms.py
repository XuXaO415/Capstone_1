from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.simple import BooleanField
# from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length
from wtforms import ValidationError
from models import User

class UserAddForm(FlaskForm):
    """Form for adding users"""
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=2, max=20)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=20), EqualTo("confirm", message="Passwords must match")])
    confirm = PasswordField("Confirm Password",  validators=[DataRequired()])
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
        
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")
    
class LoginForm(FlaskForm):
    """Login form"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    # remember_me = BooleanField("Keep me logged in")
    # submit = SubmitField('Log In')
class UserEditForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=20)])
    confirm = PasswordField("Confirm Password")
