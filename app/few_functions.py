from flask import request, jsonify, flash
from flask_login import current_user, login_user
from sqlalchemy.exc import IntegrityError
from . import db
from .models import Movie, User
from .forms import RegisterForm, LoginForm

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
                    if movie not in current_user.liked_movies:
                        movie.likes += 1
                        current_user.liked_movies.append(movie)
                        if movie in current_user.disliked_movies:
                            current_user.disliked_movies.remove(movie)
                            movie.dislikes -= 1
                        db.session.commit()
                        return {'message': f'Liked!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
                    else:
                        return {'message': f'Already liked!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
                elif action == 'dislike':
                    if movie not in current_user.disliked_movies:
                        movie.dislikes += 1
                        current_user.disliked_movies.append(movie)
                        if movie in current_user.liked_movies:
                            current_user.liked_movies.remove(movie)
                            movie.likes -= 1
                        db.session.commit()
                        return {'message': f'Disliked!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
                    else:
                        return {'message': f'Already disliked!', 'likes': movie.likes, 'dislikes': movie.dislikes, 'action': action}
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