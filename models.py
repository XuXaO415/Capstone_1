"""SQLAlchemy model for Aletheia App"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False, unique=True)
    last_name = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    user_id = db.relationship('FavoriteArticle', backref='users', lazy=True)

    def __repr__(self):
        user = self
        return f"<User #{user.id} {user.fist_name} {user.last_name} {user.email} {user.username}>"
        # return f"<User {self.id}: {self.username}. {self.password}>"


    @classmethod
    def signup(cls, first_name, last_name, email, username, password):
        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode("utf8")

        return cls(first_name=first_name, last_name=last_name, email=email, username=username, password=password)

    @classmethod
    def authenticate(cls, username, password):
        """Authenticates/validates username exists and password is correct. 
        Return user if valid; else returns false"""

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


# class Like(db.Model):
#     """User's liked stories"""

#     __tablename__ = "likes"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class LatestArticles(db.Model):
    """List lastest articles from last 2 hours"""
    
    __tablename__ = "latest_articles"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conical_url = db.Column(db.Text, nullable=False, unique=False)
    date_published = db.Column(db.Integer, nullable=False, unique=False )
    domain = db.Column(db.Text, nullable=False, unique=False)
    article_id = db.Column(db.Integer, nullable=False)
    site_type = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    
    

class TopArticle(db.Model):
    """List top article from past 30 days"""
    __tablename__ = "top_articles"
    
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.Text, nullable=False, unique=False)
    date_captured = db.Column(db.Integer, nullable=False, unique=False)
    site_type = db.Column(db.Text, nullable=False, unique=False )
    article_title = db.Column(db.Text, nullable=False, unique=False )
    upper_day = db.Column(db.Integer, nullable=False, unique=False)
    

class FavoriteArticle(db.Model):
    """User's favorite articles"""
    
    __tablename__ = "favorite_articles"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastest_id = db.Column(db.Integer, db.ForeignKey('latest_articles.id', ondelete='cascade'), unique=True)
    top_id = db.Column(db.Integer, db.ForeignKey('top_articles.id', ondelete='cascade'), unique=True)
    # title = db.Column(db.Text, db.ForeignKey('lastest_articles.id', ondelete='cascade'), nullable=False)
    # site_type = db.Column(db.Text, db.ForeignKey('top_articles.id', ondelete='cascade'), nullable=False)
    # article_title = db.Column(db.Text, db.ForeignKey('top_articles.id', ondelete='cascade'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
  