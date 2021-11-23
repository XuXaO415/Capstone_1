import os
from flask import Flask, render_template, request, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
#################################################################################
from newsapi import NewsApiClient
#################################################################################
# from forms import UserAddForm, LoginForm
from models import db, connect_db, User
#################################################################################
from secrets import API_KEY, BASE_URL
from dotenv import load_dotenv
load_dotenv()
#################################################################################
# https: // jonathansoma.com/lede/foundations-2019/classes/apis/keeping-api-keys-secret/

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///nea_db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('API_KEY', os.getenv('API_KEY'))

toolbar = DebugToolbarExtension(app)

connect_db(app)

BASE_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
CURR_USER_KEY = "curr_user"
