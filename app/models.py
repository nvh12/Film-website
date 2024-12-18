from app import db, loginManager, bcrypt
from flask_login import UserMixin

@loginManager.user_loader
def load_user(userId):
    return User.query.get(int(userId))

#Database models
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
    username = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    passwordHash = db.Column(db.String(60), nullable = False)
    
    movies = db.relationship('Movie', secondary = 'user_movie', back_populates='users')
    liked_movies = db.relationship('Movie', secondary = 'like', back_populates='liked_users')
    disliked_movies = db.relationship('Movie', secondary = 'dislike', back_populates='disliked_users')

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plainTextPass):
        self.passwordHash = bcrypt.generate_password_hash(plainTextPass).decode('utf-8')
    
    def checkPassword(self, attemptedPassword):
        return bcrypt.check_password_hash(self.passwordHash, attemptedPassword)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key = True)
    movie_title = db.Column(db.String, nullable = False)
    genres = db.Column(db.String, nullable = False)
    director_name = db.Column(db.String, nullable = False)
    actor_1_name = db.Column(db.String, nullable = False)
    actor_2_name = db.Column(db.String, nullable = False)
    actor_3_name = db.Column(db.String, nullable = False)
    release_date = db.Column(db.Date)
    poster_url = db.Column(db.String, nullable = False)
    overview = db.Column(db.String)
    runtime = db.Column(db.Integer)
    backdrop_path = db.Column(db.String)
    origin_country = db.Column(db.String)
    production = db.Column(db.String)
    likes = db.Column(db.Integer, nullable = False)
    dislikes = db.Column(db.Integer, nullable = False)

    users = db.relationship('User', secondary = 'user_movie', back_populates='movies')
    liked_users = db.relationship('User', secondary = 'like', back_populates='liked_movies')
    disliked_users = db.relationship('User', secondary = 'dislike', back_populates='disliked_movies')

class UserMovie(db.Model):
    __tablename__ = 'user_movie'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True, nullable = False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key = True, nullable = False)

class Like(db.Model):
    __tablename__ = 'like'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True, nullable = False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key = True, nullable = False)

class Dislike(db.Model):
    __tablename__ = 'dislike'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True, nullable = False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key = True, nullable = False)