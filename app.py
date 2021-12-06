import os
from flask import Flask, render_template, redirect, g, flash, session, g, url_for
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from datetime import datetime
#################################################################################
from forms import UserAddForm, LoginForm
from models import db, connect_db, User, LatestArticles, TopArticle, FavoriteArticle
#################################################################################
# from secrets import API_KEY
from dotenv import load_dotenv
load_dotenv()
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
app.config['host'] = os.getenv("host")
toolbar = DebugToolbarExtension(app)


connect_db(app)


##############################################################################
# User signup/login/logout


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
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                username=form.username.data,
                password=form.password.data
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
        user = User.authenticate(form.username.data,
                                 form.password.data
                                )

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Logs user out"""

    do_logout()
    flash("You have successfully logged out of Aletheia!", "success")
    return redirect("/login")

##############################################################################
# Homepage and error pages


@app.route("/")
def homepage():
    """Show homepage"""
    return render_template("base.html")

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template("404.html"), 404

# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template("500.html"), 500

##############################################################################


@app.route("/top-articles/<int:id>")
def top_articles(id):
    """List all top articles"""

    url = "https://api-hoaxy.p.rapidapi.com/top-articles"

    querystring = {"most_recent": "true"}

    headers = {
        'x-rapidapi-host': host,
        'x-rapidapi-key': API_KEY
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    print(response.text)


@app.route("/lates-articles")
def latest_articles():
    """List all articles from past 2 hours"""

    url = "https://api-hoaxy.p.rapidapi.com/latest-articles"

    querystring = {"past_hours": "2"}

    headers = {
        'x-rapidapi-host': host,
        'x-rapidapi-key': API_KEY
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    print(response.text)
##############################################################################
# User's favorite articles


# @app.route("/users/favorite", methods=["POST"])
# def favorite_article():
#     """Enables a user to favorite an article"""
    
#     user_id = g.user.id 
#     user = User.query.get_or_404(user_id)
    
#     if user:
        

##############################################################################
# Turn off all caching in Flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
