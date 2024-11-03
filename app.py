from flask import Flask, render_template, url_for, request, redirect, flash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
app.config['SQLALCHEMY_BINDS'] = {
    'movies' : 'sqlite:///Movies.db'
}
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
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    passwordHash = db.Column(db.String(60), nullable = False)
    #library = db.relationship('Movie', backref='ownedUser', lazy=True)
    
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plainTextPass):
        self.passwordHash = bcrypt.generate_password_hash(plainTextPass).decode('utf-8')
    
    def checkPassword(self, attemptedPassword):
        return bcrypt.check_password_hash(self.passwordHash, attemptedPassword)

class Movie(db.Model):
    __bind_key__ = 'movies'
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

#Routes
#home
@app.route('/', methods = ['POST', 'GET'])
def index():
    registerForm = RegisterForm()
    if registerForm.validate_on_submit():
        newUser = User(username = registerForm.username.data, email = registerForm.email.data, password = registerForm.password1.data)
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('index'))
    if registerForm.errors != {}:
        for err_msg in registerForm.errors.values():
            flash(f'Error: {err_msg}', category='danger')
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        attemptedUser = User.query.filter_by(username = loginForm.username.data).first()
        if attemptedUser and attemptedUser.checkPassword(attemptedPassword = loginForm.password.data):
            login_user(attemptedUser)
            flash('You are logged in as {attemptedUser.username}!', category = 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect username or password!', category = 'danger')
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    return render_template('index.html', registerForm = registerForm, loginForm = loginForm)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!', category = 'info')
    return redirect(url_for('index'))

@app.route('/results')
def results():
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    keywords = request.args.get('keywords')
    list = Movie.query.filter(Movie.movie_title.ilike(f"%{keywords}%")).all()
    return render_template('results.html', list = list)

#movies
@app.route('/movies')
def movies():
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
                           end = end,)

#watching
@app.route('/watching/<string:movie_title>')
def watching(movie_title):
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    movie = Movie.query.filter_by(movie_title = movie_title).first()
    if not movie:
        return "Movie not found", 404
    return render_template('movie-watching.html', movie = movie)

#movie description
@app.route('/description/<string:movie_title>')
def description(movie_title):
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('results', keywords = keywords))
    movie = Movie.query.filter_by(movie_title = movie_title).first()
    if not movie:
        return "Movie not found", 404
    return render_template('movie-description.html', movie = movie)

#Run
if __name__ == '__main__':
    app.run(debug = True)
