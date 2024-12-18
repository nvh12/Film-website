from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import desc
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Movie, User
from app.forms import RegisterForm, LoginForm, EmailForm, ResetForm
from datetime import datetime, timedelta
from urllib.parse import unquote
from app import db
import app.suggest_algo as suggest_algo
import app.email_sending as email_sending
import app.recovery_passcode as recovery_passcode
from app.few_functions import login_register, interactions

main_bp = Blueprint('main', __name__)

#Routes
#home
@main_bp.route('/', methods = ['POST', 'GET'])
def index(): 
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('main.results', keywords = keywords))
    mostRecent = Movie.query.order_by(desc(Movie.release_date)).limit(16).all()
    mostLiked = Movie.query.order_by(desc(Movie.likes)).limit(16).all()
    mostDisliked = Movie.query.order_by(desc(Movie.dislikes)).limit(16).all()
    return render_template('index.html', registerForm = registerForm, loginForm = loginForm,
                            mostRecent = mostRecent, mostLiked = mostLiked, mostDisliked = mostDisliked)

@main_bp.route('/recovery', methods = ['POST', 'GET'])
def recovery():
    loginForm, registerForm = login_register()
    if 'step' not in session:
        session['step'] = 1
    emailForm = EmailForm()
    resetForm = ResetForm()
    if session['step'] == 1:
        if emailForm.validate_on_submit():
            session['email'] = emailForm.email.data
            user = User.query.filter_by(email=session['email']).first()
            if user:
                code = recovery_passcode.passcode_generation()
                session['code'] = code
                session['expiry_time'] = datetime.now() + timedelta(minutes = 10)
                email_sending.send(code, [emailForm.email.data])
                flash('A recovery code has been sent to your email.', 'info')
                session['step'] = 2
                return redirect(url_for('main.recovery'))
            else:
                flash('Email address is not associated with any account!', 'info')
        return render_template('recovery.html', registerForm = registerForm, loginForm = loginForm, form = emailForm, step = 1)
    elif session['step'] == 2:
        if resetForm.validate_on_submit():
            print(f"Session code: {session.get('code')}")
            print(f"Entered code: {resetForm.code}")
            print(f"Expiry time: {session.get('expiry_time')}")
            if recovery_passcode.passcode_check(session.get('code'), resetForm.code.data) and datetime.now().replace(tzinfo=None) <= session.get('expiry_time').replace(tzinfo=None):
                user = User.query.filter_by(email=session.get('email')).first()
                user.username = resetForm.username.data
                user.password = resetForm.password1.data
                db.session.commit()
                session.clear()
                flash('Account updated!', 'info')
                return redirect(url_for('main.index'))
            else:
                flash('Incorrect or expired recovery code!', 'info')
        return render_template('recovery.html', registerForm = registerForm, loginForm = loginForm, form = resetForm, step = 2)

@main_bp.route('/reset_recovery', methods = ['POST'])
def reset_recovery():
    session.clear()
    return '', 204

@main_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!', category = 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/results', methods = ['POST', 'GET'])
def results():
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('main.results', keywords = keywords))
    keywords = request.args.get('keywords')
    list = Movie.query.filter(Movie.movie_title.ilike(f"%{keywords}%")).all()
    return render_template('results.html', list = list, registerForm = registerForm, loginForm = loginForm)

#movies
@main_bp.route('/movies', methods = ['POST', 'GET'])
def movies():
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('main.results', keywords = keywords))
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
@main_bp.route('/genre/<genre>', methods = ['POST', 'GET'])
def genre(genre):
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('main.results', keywords = keywords))
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
@main_bp.route('/watching/<movie_title>', methods = ['POST', 'GET'])
def watching(movie_title):
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('main.results', keywords = keywords))
    title = unquote(movie_title)
    movie = Movie.query.filter_by(movie_title = title).first()
    path = f"videos/{movie.id}.mp4"
    if not movie:
        return "Movie not found", 404
    list = suggest_algo.suggest(title)
    movies = Movie.query.filter(Movie.movie_title.in_(list)).all()
    return render_template('movie-watching.html', movie = movie, movies = movies, registerForm = registerForm, loginForm = loginForm, path = path)

#movie description
@main_bp.route('/description/<movie_title>', methods = ['POST', 'GET'])
def description(movie_title):
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('main.results', keywords = keywords))
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
@main_bp.route('/library', methods = ['POST', 'GET'])
def library():
    library = current_user.movies
    loginForm, registerForm = login_register()
    keywords = request.args.get('search')
    if keywords:
        return redirect(url_for('main.results', keywords = keywords))
    return render_template('library.html', registerForm = registerForm, loginForm = loginForm, library = library)