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
    
    def __repr__(self):
        return f"<User #{self.id}: {self.username}. {self.password}>"
    
    @classmethod
    def signup(cls, first_name, last_name, email, username, password):
        """Signs up new user. Hashes password & adds user to db"""
        
        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_pwd
        )
        
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Authenticates/validates username exists and password is correct. 
        Return user if valid; else returns false"""
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
    class Like(db.Model):
        """User's liked stories"""
        
        __tablename__ = "likes"
        
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    # class Headlines(db.Model):
    #     """Top trending headlines by category"""
        
    #     __tablename__ = "headlines"
    #     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #     business = db.Column(db.Text, nullable=True)
    #     entertainment = db.Column(db.Text, nullable=True)
    #     general = db.Column(db.Text, nullable=True)
    #     health = db.Column(db.Text, nullable=True)
    #     sports = db.Column(db.Text, nullable=True)
    #     technology = db.Column(db.Text, nullable=True)
        
    # class Country(db.Model):
    #     """Search news by Country"""
        
    #     __tablename__ = "countries"
        
    
    
    
    
    


