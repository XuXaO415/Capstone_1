from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()



def connect_db(app):
    """Connects to db"""

    db.app = app
    db.init_app(app)
    
    
class User(db.Model):
    """User in the system"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name  = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    
    @classmethod
    def signup(cls, first_name, last_name, email, username, pwd):
        """Signup user w/hashed password & return user"""
        
        hashed = bcrypt.generate_password_hash(pwd)
        
        hashed_utf8 = hashed.decode("utf8")
        
        return cls(first_name=first_name, last_name=last_name, email=email, username=username, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists and password is correct. 
        Return user if valid; else return false."""
        
        u = User.query.filter_by(username=username).first()
        
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False
        
class LatestArticle(db.Model):
    """List lastest articles from last 2 hours"""
    
    __tablename__ = "latest_articles"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conical_url = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False )
    domain = db.Column(db.Text, nullable=False, unique=False)
    article_id = db.Column(db.Integer, nullable=False)
    site_type = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        latest = self 
        return f"<Latest Articles {latest.id} {latest.conical_url} {latest.date_published} {latest.domain} {latest.article_id} {latest.site_type} {latest.title}"
    
    
class TopArticle(db.Model):
    """List top article from past 30 days"""
    
    __tablename__ = "top_articles"
    
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    date_captured = db.Column(db.Integer, nullable=False, unique=False)
    site_type = db.Column(db.Text, nullable=False, unique=False )
    article_title = db.Column(db.Text, nullable=False, unique=False )
    upper_day = db.Column(db.Integer, nullable=False, unique=False)
    
    def __repr__(self):
        top = self 
        return f"<Top Article {top.id} {top.canonical_url} {top.date_captured} {top.site_type} {top.article_title} {top.upper_day}>"
    
class FavoriteArticle(db.Model):
    """User's favorite articles"""
    
    __tablename__ = "favorite_articles"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Replace with backref
    lastest_id = db.Column(db.Integer, db.ForeignKey('latest_articles.id', ondelete='cascade'), unique=True)
    top_id = db.Column(db.Integer, db.ForeignKey('top_articles.id', ondelete='cascade'), unique=True)
    # title = db.Column(db.Text, db.ForeignKey('lastest_articles.id', ondelete='cascade'), nullable=False)
    # site_type = db.Column(db.Text, db.ForeignKey('top_articles.id', ondelete='cascade'), nullable=False)
    # article_title = db.Column(db.Text, db.ForeignKey('top_articles.id', ondelete='cascade'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    
    
    