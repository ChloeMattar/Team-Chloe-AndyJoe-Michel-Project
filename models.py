"""MatchIt database models: users, favorites, marathons, and marathon movies."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "account"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    favorites = db.relationship("Favorite", backref="user",cascade="all, delete-orphan")


class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("account.user_id"), nullable=False)
    movie_id = db.Column(db.String(50), nullable=False)     # TMDb movie ID
    added_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "movie_id", name="uniq_user_movie"),)


class Marathon(db.Model):
    __tablename__ = "marathon"
    marathon_id= db.Column(db.Integer, primary_key=True) # unique marathon ID
    user_id = db.Column(db.Integer, db.ForeignKey("account.user_id"), nullable=False) #identifies which user created the marathon
    title = db.Column(db.String(255), nullable=False) # name of the marathon
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False) # date and time the marathon was created 
    user=db.relationship("User", backref=db.backref("marathons", cascade="all, delete-orphan"))# SQLAlchemy relationship to the owner, One user can have multiple marathons
    
class MarathonMovie(db.Model):
    __tablename__ = "marathon_movie"
    id = db.Column(db.Integer, primary_key=True) # unique ID for the marathon movie entry
    marathon_id = db.Column(db.Integer, db.ForeignKey("marathon.marathon_id"), nullable=False) # identifies which marathon this movie belongs to
    movie_id = db.Column(db.String(50), nullable=False) # the API's id for the movie
    is_completed = db.Column(db.Boolean, default=False, nullable=False) # indicates if the movie has been watched
    marathon = db.relationship("Marathon",backref=db.backref("movies", cascade="all, delete-orphan")) # SQLAlchemy relationship to the marathon, One marathon can have multiple movies
    __table_args__ = (db.UniqueConstraint("marathon_id", "movie_id", name="uniq_marathon_movie"),) # ensures that the same movie cannot be added to the same marathon multiple times