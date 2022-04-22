import os
from re import search
from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify
from flask_login import login_user, logout_user, current_user,login_required
from flask.json.tag import JSONTag
import requests
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension
from newsapi import NewsApiClient
import datetime
import pdb
#################################################################################

from forms import UserAddForm, LoginForm, UserEditForm
from models import FavoriteArticle, db, connect_db, User, LatestArticle, TopArticle, WorldNews, Technology, Business, USPolity, Science, Health, FavoriteArticle, Likes
#################################################################################
# from secrets import api_key
from dotenv import load_dotenv
load_dotenv()
#################################################################################


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
# Add user to g
##############################################################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    # pdb.set_trace()
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

##############################################################################
# User login
##############################################################################

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

##############################################################################
# User logout
##############################################################################
def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        
##############################################################################
# Homepage
##############################################################################
@app.route("/")
def homepage():
    """Homepage"""
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')

    res = requests.get(
        f"https://newsapi.org/v2/everything?q=latin-america&q=asia&q=europe&language=en&sortBy=popularity&pageSize=5&domains=apnews.com,reuters.com,npr.org,bbc.com,economist.com,wsj.com,politifact.com,thebureauinvestigates.com&apiKey={API_SECRET_KEY}")

    world_new = res.json()['articles']
    print(res.json())
    
    res = requests.get(
        f"https://newsapi.org/v2/everything?q=top-news&language=en&sortBy=publishedAt&pageSize=5&domains=apnews.com,reuters.com,npr.org,economist.com,wsj.com,bbc.com,politifact.com,thebureauinvestigates.com&apiKey={API_SECRET_KEY}")

    latest_article = res.json()['articles']
    print(res.json())
  
#   pdb.set_trace()

    return render_template("index.html", world_news=world_new, latest_articles=latest_article)


##############################################################################
# User signup
##############################################################################

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration"""
    
    # if CURR_USER_KEY in session:
    #     del session[CURR_USER_KEY]
    
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
            return render_template("users/signup.html", form=form)
        
        do_login(user)
        return redirect('/')
    
    else:
        return render_template('/users/signup.html', form=form)
##############################################################################
# Login form
##############################################################################
        
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


##############################################################################
# User dashboard
##############################################################################
@app.route("/users/<int:user_id>")
def show_user_dashboard(user_id):

    user = User.query.get_or_404(user_id)
    # favorite_article = (FavoriteArticle
    #                     .query
    #                     .filter(FavoriteArticle.user_id == user_id)
    #                     .order_by(FavoriteArticle.timestamp.desc())
    #                     .limit(15)
    #                     .all())
    favorite_articles = (FavoriteArticle
                        .query
                        .filter(FavoriteArticle.user_id==user_id)
                        # .order_by((FavoriteArticle.id.desc())))
                        .order_by(FavoriteArticle.timestamp.desc())
                        .limit(25)
                        .all())
    return render_template('users/show.html', user=user, favorite_articles=favorite_articles)


    
##############################################################################
# User profile edit form
##############################################################################
@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """Edit user profile"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    form = UserEditForm(obj=g.user)
        
    if form.validate_on_submit():
        if User.authenticate(form.username.data, form.password.data):

            user.username = form.username.data
            user.email = form.email.data
            user.password = form.password.data
        
            db.session.add(g.user)
            db.session.commit()   
           
            
            flash("Your profile has been updated.", "success")
            return redirect(f"/users/{g.user_id}")
        else: 
            flash("Incorrect password", "danger")
            return redirect(f"/users/{g.user.id}")
    else:
        return render_template("/users/edit.html", form=form, user_id=g.user.id)
    
##############################################################################
# Delete User
##############################################################################
@app.route("/users/delete", methods=["POST"])
def delete_user():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    do_logout()
    flash (f"Your account has successfully been deleted", "success")
    
    db.session.delete(g.user)
    db.session.commit()
    return redirect("/signup")

@app.route("/users/favorite", methods=["POST"])
def user_favorite():
    
    favorite = FavoriteArticle.query\
        .filter_by(user_id=current_user)\
        .order_by((FavoriteArticle.id))
    empty = favorite is None or False if favorite is None else False
    return render_template("/users/favorite.html", favorite=favorite, empty=empty)


            
        

    # user_id = g.user.id
    # user = User.query.get_or_404(user_id)

    # if user:
    #     all_articles = FavoriteArticle.query.filter_by(user_id=user_id).order_by(FavoriteArticle.id.desc()).all()
    #     stories = []
    #     for article in all_articles:
    #         story = {'id': article.latest_id}
    #         stories.append(story)
    # return render_template("users/favorite.html", user=user, stories=stories)


@app.route("/users/favorite/<int:favorite_articles_id>", methods=["GET", "POST"])
def add_favorite(favorite_articles_id):
    """Enables a user to favorite an article"""
    
    if not g.user:
        flash("You are not the authorized user of this account", "danger")
        return redirect("/")

    
    saved_favorite = FavoriteArticle(
    user_id=g.user_id, favorite_articles_id=favorite_articles_id)
    db.session.add(saved_favorite)
    db.session.commit()
    
    flash(f"You just saved this article!", "success")
    # return render_template("/users/favorite.html")
    # return redirect(url_for("/users/dashboard"))
    return render_template("/users/favorite.html", saved_favorite=saved_favorite)


# @app.route("/users/<int:user_id>/favorite", methods=[])
# def user_favorites(user_id):
#     """Shows a list of a user's favored articles"""
    
#     if not g.user:
#         return redirect("/")
    
#     user = User.query.get_or_404(user_id)
#     return render_template("/users/favorite.html", user=user)
    
    

@app.route("/users/delete/<int:favorite_articles_id>", methods = ["Get", "POST"])
def delete_favorite(favorite_articles_id):
    if not g.user:
        flash("Access unauthorized!", "danger")
        return redirect("/")
    user_favorite_article = FavoriteArticle.query.filter_by(favorite_articles_id=str(favorite_articles_id),user_id=str(g.user.id)).first()
    
    db.session.delete(user_favorite_article)
    db.session.commit()
    
    return redirect(f"/users/favorite")




##############################################################################
# Upon successful logout, redirects user to login page
##############################################################################

@app.route("/logout")
def logout():

    do_logout()
    flash("You have successfully logged out", "success")
    
    return redirect(url_for("login"))
    # return redirect('/login')

##############################################################################
# Super simple 404 page
##############################################################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

##############################################################################
# Homepage quick link that displays latest news
##############################################################################


@app.route("/latest_articles", methods =["GET", "POST"])
def show_latest_articles():
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    # url = ('https://newsapi.org/v2/top-headlines?' 'language=en' 'qinTitle=query' 'apiKey={API_SECRET_KEY}')
    # res = requests.get(url)
    # print(res.text)
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=general&country=us&pageSize=10&apiKey={API_SECRET_KEY}")
    # pdb.set_trace()
    latest_art = res.json()['articles']
        
    print(res.json())
    
    
    return render_template("latest_articles.html", latest_articles=latest_art)
##############################################################################


# @app.route("/latest_articles/<int:latest_article_id>", methods=["GET", "POST"])
# def latest_articles(latest_article_id):
#     API_SECRET_KEY = os.getenv('API_SECRET_KEY')

#     # url = ('https://newsapi.org/v2/top-headlines?' 'language=en' 'qinTitle=query' 'apiKey={API_SECRET_KEY}')
#     # res = requests.get(url)
#     # print(res.text)
#     res = requests.get(
#         f"https://newsapi.org/v2/top-headlines?category=general&country=us&pageSize=10&apiKey={API_SECRET_KEY}")

#     # latest_art = res.json()['articles']
#     latest_article = LatestArticle.query.get(latest_article_id)

#     print(res.json())

#     return render_template("latest_articles.html", latest_article=latest_article)
##############################################################################
@app.route("/world_news", methods=["GET", "POST"])
def show_world_news():
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    # url = ('https://newsapi.org/v2/top-headlines?' 'language=en' 'qinTitle=query' 'pageSize=10' 'apiKey={API_SECRET_KEY}')
    # res = requests.get(url)
    
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?q=international&language=en&pageSize=15&apiKey={API_SECRET_KEY}")
    
    world_new =res.json()['articles']
 
    print(res.json())
    
    return render_template("article_list.html", articles=world_new, title='World News')
##############################################################################
# Homepage quick link that displays tech news
##############################################################################

@app.route("/technology", methods=["GET", "POST"])
def show_tech_news():
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=technology&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    tech_news = res.json()['articles']
    print(res.json())
    return render_template("article_list.html", articles=tech_news, title='Technology')
    
    
@app.route("/business", methods=["GET","POST"])
def show_business_news():
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=business&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    business_news = res.json()['articles']
    print(res.json())
    return render_template("article_list.html", articles=business_news, title='Business')


@app.route("/us_news", methods=["GET", "POST"])
def show_us_news():
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    national_news = res.json()['articles']
    print(res.json())
    return render_template("article_list.html", articles=national_news, title='U.S News')


@app.route("/science", methods=["GET", "POST"])
def show_science_news():
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=science&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    science_article = res.json()['articles']
    print(res.json())
    return render_template("article_list.html", articles=science_article, title='Science')


@app.route("/health", methods=["GET", "POST"])
def show_health_news():
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    res = requests.get(
        f"https://newsapi.org/v2/top-headlines?category=health&country=us&pageSize=15&apiKey={API_SECRET_KEY}")
    health_news = res.json()['articles']
    print(res.json())
    
    return render_template("article_list.html", articles=health_news, title='Health')
##############################################################################
# Search box for all news
##############################################################################
@app.route("/search", methods=["GET","POST"])
def search_all_articles():
   
    HOST = os.getenv('HOST')
    API_KEY = os.getenv('API_KEY')
    API_SECRET_KEY = os.getenv('API_SECRET_KEY')
    
    querystring = {
        "query": request.args['q'], "sort_by": "relevant", "use_lucene_syntax": "true"}
    
    latestquery = {
        "query": request.args['q'],  "sort_by": "recent", "use_lucene_syntax": "true"}
    
    querytitle = {"query": "+title:\"China Is Mining Bitcoin Underground: Report\"",
                  "sort_by": "recent", "use_lucene_syntax": "true"}

    
    headers = {
        'x-rapidapi-host': HOST,
        'x-rapidapi-key': API_KEY
    }
    
    url = ('https://newsapi.org/v2/everything?'
           'qinTitle=query'
           'apiKey={API_SECRET_KEY}')

    relevant_response = requests.get("https://api-hoaxy.p.rapidapi.com/articles", headers=headers,
                            params=querystring)
    
    recent_response = requests.get("https://api-hoaxy.p.rapidapi.com/articles", headers=headers,
                            params=latestquery)
    
    response = requests.get(url)
    
    relevant_articles = relevant_response.json()
    rel_art = relevant_articles['articles'][0:10]
    for art in rel_art:
        res = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_SECRET_KEY}"
        # res = requests.get(f"https://newsapi.org/v2/everything?qinTitle=China Is Mining Bitcoin Underground: Report&apiKey={API_SECRET_KEY}"
                                    )
        print(res.json()['articles'][0]['description'])
        art['description'] = res.json()['articles'][0]['description']
        
    # recent_articles = recent_response.json()
    # rec_art = recent_articles['articles']['author']['title']['description'][0:10]
    #     for r_art in rec_art:
    #         resp = request.get(f'')

    # recent_articles = recent_response.json()
    
    title_request = response.json()
    print (response.text)

    # return jsonify(top_articles)
   
    return render_template("top_articles.html", top_articles=relevant_articles['articles'][0:10], titlequery=title_request)


    return render_template("latest_articles.html", latest_articles=recent_articles['articles'][0:10], titlequery=title_request)
##############################################################################
@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


##############################################################################

