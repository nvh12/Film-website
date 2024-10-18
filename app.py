from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db1.dl'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    userName = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    
    def __repr__(self):
        return '<User %s>' % self.userName
        # %r for debugging

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/watching')
def watching():
    return render_template('movie-watching.html')

@app.route('/description')
def description():
    return render_template('movie-description.html')

@app.route('/creatingaccount', methods = ['POST', 'GET'])
def form():
    if request.method == 'POST':
        email = request.form.get('email')
        userName = request.form.get('userName')
        password = request.form.get('password')

        checkByEmail = db.session.query(User).filter_by(email = email).first()
        checkByUsername = db.session.query(User).filter_by(userName = userName).first()
        
        if checkByEmail:
            flash('Email already used')
            return redirect('/CreateAccount')
        elif checkByUsername:
            flash('Username already used')
            return redirect('/CreateAccount')
        else:
            newUser = User(userName = userName, email = email, password = password)
            db.session.add(newUser)
            db.session.commit()
            flash('Account created')
    else:
        return render_template('form.html')
        
if __name__ == '__main__':
    app.run(debug = True)
