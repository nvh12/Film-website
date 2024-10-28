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
    id = db.Column(db.Integer, primary_key = True)
    movie_title = db.Column(db.String, nullable = False)
    genres = db.Column(db.String, nullable = False)
    director_name = db.Column(db.String, nullable = False)
    actor_1_name = db.Column(db.String, nullable = False)
    actor_2_name = db.Column(db.String, nullable = False)
    actor_3_name = db.Column(db.String, nullable = False)
    release_date = db.Column(db.Date)
    poster_url = db.Column(db.String, nullable = False)
    over_view = db.Column(db.String)

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

#Create database tables
with app.app_context():
    db.create_all()

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
    return render_template('index.html', registerForm = registerForm, loginForm = loginForm)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!', category = 'info')
    return redirect(url_for('index'))

#movies
@app.route('/movies')
def movies():
    return render_template('movies.html')

#watching
@app.route('/watching')
def watching():
    return render_template('movie-watching.html')

#movie description
@app.route('/description')
def description():
    return render_template('movie-description.html')


#Run
if __name__ == '__main__':
    app.run(debug = True)
