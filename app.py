import os
from flask import Flask, render_template, redirect, g, flash, session, g, url_for
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
#################################################################################
from forms import UserAddForm, LoginForm
from models import db, connect_db, User
#################################################################################
# from secrets import API_KEY, BASE_URL
# from dotenv import load_dotenv
# load_dotenv()
#################################################################################
# https: // jonathansoma.com/lede/foundations-2019/classes/apis/keeping-api-keys-secret/

CURR_USER_KEY = "curr_user"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///nea_db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('API_KEY', os.getenv('API_KEY'))
# app.config['SECRET_KEY'] = 'API_KEY'
toolbar = DebugToolbarExtension(app)

connect_db(app)

# BASE_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
# # url = f"https://api-hoaxy.p.rapidapi.com/latest-articles"

##############################################################################
#User signup/login/logout

@app.before_request
def add_user_to_g():
    """When logged in, adds curr_user to Flask global"""
    
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        
    else:
        g.user = None
        
        
def do_login(user):
    """Logs in user"""
    
    session[CURR_USER_KEY] = user.id 
    
def do_logout():
    """Logs out user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handles user signup; stores it in db"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserAddForm()
    
    if form.validate_on_submit():
        try:
            user = User.signup( 
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email = form.email.data,
                username = form.username.data,
                password = form.password.data
            )
            db.session.commit()
            
        except IntegrityError:
            flash("Sorry, that username is taken.", "danger")
            return render_template("users/signup.html", form=form)
        
        do_login(user)
        return redirect("/")
    
    else:
        return render_template("users/signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data,
        password = form.password.data

        user = User.authenticate(username=username, password=password)

        if user:
            do_login(user)
            flash(f"Welcome back {user.username}", "success")
            return redirect("/")

        flash("Invalid credentials", "danger")

    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Logs user out"""

    do_logout()
    flash("You have successfully logged out of Aletheia!", "success")
    return redirect("/")
        
##############################################################################
# Homepage and error pages
        
@app.route("/")
def homepage():
    return render_template("base.html")

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template("404.html"), 404

##############################################################################



# @app.route("/list-articles")
# def search():
    
        
##############################################################################
#Turn off all caching in Flask
@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
