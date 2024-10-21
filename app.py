from flask import Flask, render_template, url_for, request, redirect, flash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db1.db'
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
@app.route('/')
def index():
    return render_template('index.html')

#create account
@app.route('/register', methods = ['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        newUser = User(username = form.username.data, email = form.email.data, password = form.password1.data)
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('index'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error: {err_msg}', category='danger')
    return render_template('form.html', form = form)

#login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attemptedUser = User.query.filter_by(username = form.username.data).first()
        if attemptedUser and attemptedUser.checkPassword(attemptedPassword = form.password.data):
            login_user(attemptedUser)
            flash('You are logged in as {attemptedUser.username}!', category = 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect username or password!', category = 'danger')
    return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!', category = 'info')
    return redirect(url_for('index'))

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
