from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_manager


db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connects to db"""

    db.app = app
    db.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):
    
#     """Flask login user session management"""
    
#     return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User in the system"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    

    favorite_articles = db.relationship('FavoriteArticle')
    likes = db.relationship('User', secondary='likes')

    @classmethod
    def signup(cls, first_name, last_name, email, username, pwd):
        """Signup user w/hashed password & return user"""

        hashed = bcrypt.generate_password_hash(pwd)

        hashed_utf8 = hashed.decode("utf8")

        user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=hashed_utf8)
        # return cls(first_name=first_name, last_name=last_name, email=email, username=username, password=hashed_utf8)
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists and password is correct.
        Return user if valid; else return false."""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False


class LatestArticle(db.Model):
    """List lastest articles from last 2 hours"""

    __tablename__ = "latest_articles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conical_url = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    domain = db.Column(db.Text, nullable=False, unique=False)
    article_id = db.Column(db.Integer, nullable=False)
    site_type = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    url_image = db.Column(db.Text)

    def __repr__(self):
        latest_article = self
        return f"<Latest Article {latest_article.id} {latest_article.conical_url} {latest_article.date_published} {latest_article.domain} {latest_article.article_id} {latest_article.site_type} {latest_article.title}"


class TopArticle(db.Model):
    """List top article from past 30 days"""

    __tablename__ = "top_articles"
    """ __searchable__ = "top_articles" """

    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    site_type = db.Column(db.Text, nullable=False, unique=False)
    article_title = db.Column(db.Text, nullable=False, unique=False)
    upper_day = db.Column(db.Integer, nullable=False, unique=False)
    description = db.Column(db.Text)
    title = db.Column(db.Text)
    url_image = db.Column(db.Text)

    def __repr__(self):
        top_article = self
        return f"<Top Article {top_article.id} {top_article.description} {top_article.title} {top_article.canonical_url} {top_article.date_published} {top_article.site_type} {top_article.article_title} {top_article.upper_day}>"

class WorldNews(db.Model):
    """ List World news articles -- from NewsAPI"""
    
    __tablename__ = "world_news"

    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    article_title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    url_image = db.Column(db.Text)
    
    def __repr__(self):
        world_article = self
        return f"<World Article {world_article.id} {world_article.canonical_url}{world_article.author}{world_article.date_published}{world_article.article_title}{world_article.description}{world_article.url_image}"

class Technology(db.Model):
    """List tech news -- from NewsAPI"""
    
    __tablename__ = "tech_news"
    
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    article_title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    url_image = db.Column(db.Text)
    
    def __repr__(self):
        technology_article = self
        return f"<Technology Article {technology_article.id}{technology_article.canonical_url}{technology_article.author}{technology_article.date_published}{technology_article.article_title}{technology_article.description}{technology_article.url_image}"
class Business(db.Model):
    """List latest business News"""
    
    __tablename__ = "business_news"
    
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    article_title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    url_image = db.Column(db.Text)
    
    def __repr__(self):
        business_article = self
        return f"<Business Article {business_article.id}{business_article.canonical_url}{business_article.author}{business_article.date_published}{business_article.article_title}{business_article.description}{business_article.url_image}"
    
class USPolity(db.Model):
    """List political news from the U.S"""
    
    __tablename__ = "us_news"
    
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    article_title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    url_image = db.Column(db.Text)
    
    def __repr__(self):
        us_pol = self
        return f"<U.S Politics {us_pol.id}{us_pol.canonical_url}{us_pol.author}{us_pol.date_published}{us_pol.article_title}{us_pol.description}{us_pol.url_image}"
    
class Science(db.Model):
    """List latest science news"""
    
    __tablename__ = "science_news"
    
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    article_title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    url_image = db.Column(db.Text)
    
    def __repr__(self):
        science_article = self
        return f"<Science Article {science_article.id}{science_article.canonical_url}{science_article.author}{science_article.date_published}{science_article.article_title}{science_article.description}{science_article.url_image}"
    
class Health(db.Model):
    """List latest health news"""
    
    __tablename__ = "health_news"
    
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    author = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False)
    article_title = db.Column(db.Text, nullable=False, unique=False)
    description = db.Column(db.Text)
    url_image = db.Column(db.Text)

    def __repr__(self):
        health_article = self
        return f"<Health Article {health_article.id}{health_article.canonical_url}{health_article.author}{health_article.date_published}{health_article.article_title}{health_article.description}{health_article.url_image}"
    
    
# class FavoriteArticle(db.Model):
#     """User's favorite articles"""
    
#     __tablename__ = "favorite_articles"
    
#     id = db.Column(db.Integer, primary_key=True)
#     # Replace with backref
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade')) 
#     lastest_id = db.Column(db.Integer, db.ForeignKey('latest_articles.id', ondelete='cascade'), unique=True)
#     top_id = db.Column(db.Integer, db.ForeignKey('top_articles.id', ondelete='cascade'), unique=True)
#     title = db.Column(db.Text, db.ForeignKey('lastest_articles.id', ondelete='cascade'), nullable=False)
#     # site_type = db.Column(db.Text, db.ForeignKey('top_articles.id', ondelete='cascade'), nullable=False)
#     article_title = db.Column(db.Text, db.ForeignKey('top_articles.id', ondelete='cascade'), nullable=False)

    
#     def __repr__(self):
#         favorites = self
#         return f"<Favorite {favorites.id}{favorites.canonical_url}{favorites.author}{favorites.date_published}{favorites.article_title}{favorites.description}{favorites.url_image}"



# class FavoriteArticle(db.Model):
#     """ user's favorite articles"""
#     __tablename__ = "favorite_articles"
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
#     timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
#     latest_id = db.Column(db.Integer, db.ForeignKey('latest_articles.id', ondelete='cascade'), unique=True)
#     top_id = db.Column(db.Integer, db.ForeignKey('top_articles.id', ondelete='cascade'),unique=True)
#     world_id = db.Column(db.Integer, db.ForeignKey('world_news.id', ondelete='cascade'),unique=True)
#     technology_id = db.Column(db.Integer, db.ForeignKey('tech_news.id', ondelete='cascade'), unique=True)
#     business_id = db.Column(db.Integer, db.ForeignKey('business_news.id', ondelete='cascade'), unique=True)
#     us_id = db.Column(db.Integer, db.ForeignKey('us_news.id', ondelete='cascade'), unique=True)
#     science_id = db.Column(db.Integer, db.ForeignKey('science_news.id', ondelete='cascade'),unique=True)
#     health_id = db.Column(db.Integer, db.ForeignKey('health_news.id', ondelete='cascade'), unique=True)
#     user = db.relationship('User')
    
class Likes(db.Model):
        
    __tablename__ = 'likes'
        
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    favorite_article = db.Column(db.Integer, db.ForeignKey('favorite_articles.id', ondelete='cascade'))
        
class FavoriteArticle(db.Model):
    """ user's favorite articles"""
    
    __tablename__ = "favorite_articles"
        
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    source = db.Column(db.Text)
    author = db.Column(db.Text)
    title = db.Column(db.Text)
    description  = db.Column(db.Text)
    users = db.relationship('User', backref='favorite_article')
    
    
    
    