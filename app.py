from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
from urllib.parse import unquote
import suggest_algo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '2a0f76e24979a57e'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
loginManager = LoginManager(app)

@loginManager.user_loader
def load_user(userId):
    return User.query.get(int(userId))


#Databases
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
    username = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    passwordHash = db.Column(db.String(60), nullable = False)
    
    movies = db.relationship('Movie', secondary = 'user_movie', back_populates = 'users')

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

    users = db.relationship('User', secondary = 'user_movie', back_populates = 'movies')

class UserMovie(db.Model):
    __tablename__ = 'user_movie'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True, nullable = False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key = True, nullable = False)


#Forms
class RegisterForm(FlaskForm):
    username = StringField(label='Username: ', validators=[Length(min=4, max=40), DataRequired()])
    email = StringField(label='Email: ', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password: ', validators=[Length(min=8), DataRequired()])
    password2 = PasswordField(label='Confirm password: ', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='Username: ', validators=[Length(min=4, max=40), DataRequired()])
    password = PasswordField(label='Password: ', validators=[Length(min=8), DataRequired()])
    submit = SubmitField(label='Log in')


#A few functions
#login and register
def login_register():
    registerForm = RegisterForm()
    loginForm = LoginForm()
    if registerForm.validate_on_submit():
        newUser = User(username = registerForm.username.data, email = registerForm.email.data, password = registerForm.password1.data)
        try:
            db.session.add(newUser)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  
            if User.query.filter_by(email=registerForm.email.data).first():
                flash('This email is already used!', category='danger')
            elif User.query.filter_by(username=registerForm.username.data).first():
                flash('This username is already taken!', category='danger')
            else:
                flash('Some fields are missing or there was an error with your submission. Please check and try again.', category='danger')
    if loginForm.validate_on_submit():
        attemptedUser = User.query.filter_by(username = loginForm.username.data).first()
        if attemptedUser and attemptedUser.checkPassword(attemptedPassword = loginForm.password.data):
            login_user(attemptedUser)
            flash(f'You are logged in as {attemptedUser.username}!', category = 'success')
        else:
            flash('Incorrect username or password!', category = 'danger')
    return loginForm, registerForm

#handling likes, dislikes and library movie additions/removal
def interactions(movie):
    if request.method == 'POST':
        if current_user.is_authenticated:
            if request.is_json:
                data = request.get_json()
                action = data.get('action')
                if action == 'like':
                    movie.likes += 1
                    db.session.commit()
                    return {'message': f'Liked!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
                elif action == 'dislike':
                    movie.dislikes += 1
                    db.session.commit()
                    return {'message': f'Disliked!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
                elif action == 'add':
                    if movie not in current_user.movies:
                        current_user.movies.append(movie)
                        db.session.commit()
                        return {'message': f'Movie added to library!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
                elif action == 'remove':
                    if movie in current_user.movies:
                        current_user.movies.remove(movie)
                        db.session.commit()
                        return {'message': f'Movie removed from library!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
        else:
            return {'message': f'Log in to access features', 'likes': movie.likes, 'dislikes': movie.dislikes}


#Routes
#home
@app.route('/', methods = ['POST', 'GET'])
def index(): 
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    mostRecent = Movie.query.order_by(desc(Movie.release_date)).limit(16).all()
    mostLiked = Movie.query.order_by(desc(Movie.likes)).limit(16).all()
    mostDisliked = Movie.query.order_by(desc(Movie.dislikes)).limit(16).all()
    return render_template('index.html', registerForm = registerForm, loginForm = loginForm,
                            mostRecent = mostRecent, mostLiked = mostLiked, mostDisliked = mostDisliked)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!', category = 'info')
    return redirect(url_for('index'))

@app.route('/results', methods = ['POST', 'GET'])
def results():
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    keywords = request.args.get('keywords')
    list = Movie.query.filter(Movie.movie_title.ilike(f"%{keywords}%")).all()
    return render_template('results.html', list = list, registerForm = registerForm, loginForm = loginForm)

#movies
@app.route('/movies', methods = ['POST', 'GET'])
def movies():
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    noMovies = 48
    page = request.args.get('page', default = 1, type  = int)
    movieQuery = Movie.query.paginate(page = page, per_page = noMovies, error_out = False)
    start = max(1, page - 5)
    end = min(movieQuery.pages, page + 5)
    return render_template('movies.html',
                            movies = movieQuery.items,
                            curPage = movieQuery.page,
                            next = movieQuery.has_next,
                            prev = movieQuery.has_prev,
                            nextPage = movieQuery.next_num,
                            prevPage = movieQuery.prev_num,
                            noPages = movieQuery.pages,
                            start = start,
                            end = end,
                            registerForm = registerForm, loginForm = loginForm)

#genre
@app.route('/genre/<genre>', methods = ['POST', 'GET'])
def genre(genre):
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    noMovies = 48
    page = request.args.get('page', default = 1, type  = int)
    genreList = Movie.query.filter(Movie.genres.ilike(f"%{genre}%")).paginate(page=page, per_page=noMovies, error_out=False)
    start = max(1, page - 5)
    end = min(genreList.pages, page + 5)
    return render_template('genre.html', 
                            genre = genre,
                            movies = genreList.items, 
                            next = genreList.has_next,
                            prev = genreList.has_prev,
                            nextPage = genreList.next_num,
                            prevPage = genreList.prev_num,
                            noPages = genreList.pages,
                            start = start,
                            end = end,
                            registerForm = registerForm, loginForm = loginForm)

#watching
@app.route('/watching/<movie_title>', methods = ['POST', 'GET'])
def watching(movie_title):
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    title = unquote(movie_title)
    movie = Movie.query.filter_by(movie_title = title).first()
    path = f"videos/{movie.id}.mp4"
    if not movie:
        return "Movie not found", 404
    list = suggest_algo.suggest(title)
    movies = Movie.query.filter(Movie.movie_title.in_(list)).all()
    return render_template('movie-watching.html', movie = movie, movies = movies, registerForm = registerForm, loginForm = loginForm, path = path)

#movie description
@app.route('/description/<movie_title>', methods = ['POST', 'GET'])
def description(movie_title):
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    title = unquote(movie_title)
    movie = Movie.query.filter_by(movie_title = title).first()
    if not movie:
        return "Movie not found", 404
    list = suggest_algo.suggest(title)
    movies = Movie.query.filter(Movie.movie_title.in_(list)).all()
    interaction = interactions(movie)
    if interaction:
        return interaction
    return render_template('movie-description.html', movie = movie, movies = movies, registerForm = registerForm, loginForm = loginForm)

#user library
@app.route('/library', methods = ['POST', 'GET'])
def library():
    library = current_user.movies
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    return render_template('library.html', registerForm = registerForm, loginForm = loginForm, library = library)

#Run
if __name__ == '__main__':
    app.run(debug = True)
