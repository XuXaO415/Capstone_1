import os
from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify
from flask.json.tag import JSONTag
import requests
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension
from newsapi import NewsApiClient
import pdb
#################################################################################

from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, LatestArticle, TopArticle, FavoriteArticle
#################################################################################
# from secrets import api_key
from dotenv import load_dotenv
load_dotenv()
#################################################################################

# TA_URL = f'https://api-hoaxy.p.rapidapi.com/top-articles'

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///nea_db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('API_KEY', 'This is classified information')

toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    # pdb.set_trace()
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        
@app.route("/")
def homepage():
    """Homepage"""
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration"""
    
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    
    form = UserAddForm()
    
    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name = form.username.data,
                last_name = form.last_name.data,
                email = form.email.data,
                username = form.username.data,
                pwd = form.password.data,
                
            )
            db.session.add(user)
            db.session.commit()
            
        except IntegrityError:
            flash("Sorry, that username is already taken", "error")
            return render_template('users/signup.html', form=form)
        
        do_login(user)
        return redirect('/')
    
    else:
        return render_template('/users/signup.html', form=form)
        
@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        
        flash("Invalid credentials.", "danger")
        
    return render_template('users/login.html', form=form)

@app.route("/logout")
def logout():
    do_logout()
    flash("You have successfully logged out", "success")
    return redirect('/')

##############################################################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

##############################################################################
@app.route("/search")
def show_top_articles():
   
    HOST = os.getenv('HOST')
    API_KEY = os.getenv('API_KEY')
    TA_URL = "https://api-hoaxy.p.rapidapi.com/top-articles"
    # articles = request.args["articles"]
    # print(API_KEY)
    

    querystring = {
    "query": request.args['q'], "sort_by": "relevant", "use_lucene_syntax": "true"}
    
    latestquery = {
        "query": request.args['q'], "sort_by": "recent", "use_lucene_syntax": "true"}

    
    headers = {
        'x-rapidapi-host': "api-hoaxy.p.rapidapi.com",
        'x-rapidapi-key': "d8313e232amsh5a802c2be2cf4d8p166013jsn2c6c9bae4858"
    }

    response = requests.get("https://api-hoaxy.p.rapidapi.com/articles", headers=headers,
                            params=querystring)
    
    latestresponse = requests.get("https://api-hoaxy.p.rapidapi.com/articles", headers=headers,
                            params=latestquery)
    top_articles = response.json()
    latest_articles= latestresponse.json()
    print(response.text)
    # return jsonify(top_articles)
    # pdb.set_trace()
    return render_template("top_articles.html", top_articles=top_articles['articles'], latest_articles=latest_articles['articles'])



@app.route("/search/newsapi", methods=["GET", "POST"])
def search_top_articles():

    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    response = requests.get(f"https://newsapi.org/v2/top-headlines?q={request.args['q']}&apiKey={API_SECRET_KEY}"
        )
    
    top_headlines = response.json()
    return jsonify(top_headlines)



        
    

# DO NOT USE
# @app.route("/search")
# def search_articles():
#     search = request.args.get("q")
#     top_articles = TopArticle.query.all()
#     return render_template('index.html', top_articles=top_articles)


# @app.route("/top-headlines")
# def show_top_headlines():

#     # HOST = os.getenv('HOST')
#     API_SECRET_KEY = os.getenv('API_SECRET_KEY')
#     TA_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_SECRET_KEY}"
#     # headlines = request.args.get["headlines"]


#     response = requests.get(TA_URL)
#     top_headlines = response.json()
#     # print(response.text)
#     return jsonify(top_headlines)
#     return render_template("top_headlines.html", headlines=top_headlines)

    
# @app.route("/top-articles")
# def list_top_articles():
#     """List top articles from last 30 days"""
    
#     top_articles = TopArticle.query.all()
    
#     # TA_URL = os.getenv('TA_URL')
#     HOST = os.getenv('HOST')
#     API_KEY = os.getenv('API_KEY')
    
#     TA_URL = "https://api-hoaxy.p.rapidapi.com/top-articles"

    
#     querystring = {"most_recent": "true"}
    
#     headers = {
#         'x-rapidapi-host': 'HOST',
#         'x-rapidapi-key': 'API_KEY' 
#         }
#     top_articles = request.args.get["top_articles"]
#     response = requests.get(TA_URL, headers=headers, params=querystring)
#     # print(response.json())
#     top_articles = request.args.get["top_articles"]
#     return jsonify(top_articles)
#     # print(response.json())
    
#     return render_template("top_articles.html", top_articles=top_articles)
    
# @app.route("/latest-articles/<string:past_hours>")
# def list_latest_articles(past_hours):
#     """Returns lastest articles from the past 2 hours"""
    
#     latest_articles = LatestArticle.query.all()
    
#     HOST = os.getenv('HOST')
#     API_KEY = os.getenv("API_KEY")
    
#     LA_URL = "https://api-hoaxy.p.rapidapi.com/latest-articles"
    
#     querystring = {"past_hours": "2"}
    
#     headers = {
#         'x-rapid-host': 'HOST',
#         'x-rapid-key': 'API_KEY'
#     }
    
#     response = requests.request("GET", LA_URL, headers=headers, params=querystring)
#     print(response.json())
    
    
#     return render_template("latest_articles.html", latest_articles=latest_articles)

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
