import os
from flask import Flask, render_template, redirect, g, flash, session, g, url_for, request
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
#################################################################################
from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, LatestArticles, TopArticle, FavoriteArticle
#################################################################################
# from secrets import API_KEY
from dotenv import load_dotenv
load_dotenv()
#################################################################################
# https: // jonathansoma.com/lede/foundations-2019/classes/apis/keeping-api-keys-secret/
import pdb

CURR_USER_KEY = "curr_user"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///nea_db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
API_KEY = os.getenv('API_KEY')
# app.config['SECRET_KEY'] = 'API_KEY'
host = os.getenv("host")
toolbar = DebugToolbarExtension(app)


connect_db(app)
# db.create_all()


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
            db.session.add(user)
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
        # user = User.authenticate(form.username.data, form.password.data)
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        # pdb.set_trace()
        
        if user:
            do_login(user)
            flash(f"Welcome back {user.username}!", "success")
            return redirect("/")
        
        flash("Invalid credentials!", "danger")
        
    return render_template("users/login.html", form=form)
            
    
    # Salt not working
    # form = LoginForm()

    # if form.validate_on_submit():
    #     user = User.authenticate(form.username.data,
    #                              form.password.data
    #                             )

    #     if user:
    #         do_login(user)
    #         flash(f"Welcome back {user.username}!", "success")
    #         return redirect("/")

    #     flash("Invalid credentials!", "danger")

    # return render_template("users/login.html", form=form)
    
    # TODO: Make user profile page
# @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
# def edit_user(user_id):
#     """Shows user edit form and handle edit"""
    
#     user = User.query.get_or_404(user_id)
    
#     form = UserEditForm(user=user)
    
#     if form.validate_on_submit():
#         user.email = form.email.data
#         user.username = form.username.data
#         user.password = form.password.data
        
#         # db.session.add(user)
#         db.session.commit()
        
#         flash(f"User {user_id} successfully updated")
#         return redirect(f"/users/{user_id}/edit")
    
#     else:
#         return render_template("/users/edit.html", form=form)
        

@app.route('/users/edit', methods=["GET", "POST"])
def edit_user():
    """Edit user profile"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    user = g.user
    form = UserEditForm(obj=g.user)

    if form.validate_on_submit():
        user =  User.authenticate(form.username.data, form.password.data)
        
        if user:
            user.username = form.username.data
            user.email = form.email.data
            user.password = form.password.data
            
            db.session.add(user)
            db.session.commit()
            
            flash("Your profile has been updated", "success")
            return redirect(f"/user/{g.user.id}")
        else:
            flash("Incorrect credentials", "danger")
            return redirect(f"/users/{g.user.id}")
    else:
            return render_template("users/edit.html", form=form)
            

# @app.route("/users/<int:user_id>")
# def user_profile(user_id):
#     user = User.query.get(user_id)
#     if g.user.id != user.id:
#         return redirect(f"/users/{g.user.id}")
    
#     if not g.user:
#         flash("Unauthorized Access, you must be logged in to view this content", "danger")
#         return redirect("/login")
    
#     return render_template("users/profile.html", user=user)



@app.route("/logout")
def logout():
    """Logs user out"""

    do_logout()
    flash("You have successfully logged out of Aletheia!", "success")
    return redirect("/login")


##############################################################################
# Homepage and error pages

@app.route("/")
def index():
    
    return render_template("index.html")

    
# @app.route("/homepage")
# def homepage():
#     """Show homepage"""
#     return render_template("base.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

##############################################################################
# @app.route("/top")
# def top_articles():
#     render_template("top-articles.html")

@app.route("/top-articles")
def get_top_articles(): 
    """List all top articles"""
    host = os.getenv('host')
    API_KEY = os.getenv('API_KEY')
    URL = os.getenv('URL')
    # querystring = os.getenv('querystring')
    
    
    # pdb.set_trace()
    # print(f"host")
    
    # querystring = {"most_recent": "true"}
    

    # headers = {
    #     'x-rapidapi-host': host,
    #     'x-rapidapi-key': API_KEY
    # }

    # response = requests.request(
    #     "GET", URL, headers=headers, params=querystring)
    # # pdb.set_trace()
    
    # data = response.json()
    
    # return render_template("top-articles.html")
    # print(response.text)
    
    response = requests.get(URL, host=host)
    print 
    response.json()
    
    


# @app.route("/latest-articles")
# def latest_articles():
#     """List all articles from past 2 hours"""

#     url = "https://api-hoaxy.p.rapidapi.com/latest-articles"

#     querystring = {"past_hours": "2"}

#     headers = {
#         'x-rapidapi-host': host,
#         'x-rapidapi-key': API_KEY
#     }

#     response = requests.request(
#         "GET", url, headers=headers, params=querystring)

#     print(response.text)
    

##############################################################################
# User's favorite articles


# @app.route("/users/favorite", methods=["GET", POST"])
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
