from datetime import datetime
from werkzeug.urls import url_parse

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from webapp import app, db
from webapp.models import User
from webapp.utils import store_image
from webapp.forms import LoginForm, RegistrationForm, UpdateProfileForm


posts = [
    {
        'author': {'username': 'Mohamed Abdelmagid'},
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': {'username': 'Ali Mohamed Abdelgadir'},
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home Page', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            image_file = store_image(form.picture.data)
            current_user.image_file = image_file
             
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data

        db.session.commit()
        flash('Your profile has been updated !', 'info')
        return redirect(url_for('account', username=current_user.username))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me

    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('edit_profile.html', title='Edit Profile', image_file=image_file, form=form)


@app.route("/account/<string:username>", methods=['GET', 'POST'])
@login_required
def account(username):
    user = User.query.filter_by(username=username).first_or_404()
    image_file = url_for('static', filename='pics/' + user.image_file)
    return render_template('account.html', user=user, image_file=image_file, posts=posts)

@app.route("/follow/<string:username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user == current_user:
            flash('You cannot follow yourself !!')
            return redirect(url_for('account', username=username))

        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('account', username=username))
    else:
        flash('User {} not found.'.format(username))
        return redirect(url_for('home'))

@app.route("/unfollow/<string:username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user == current_user:
            flash('You cannot unfollow yourself !!')
            return redirect(url_for('account', username=username))

        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {} anymore !'.format(username))
        return redirect(url_for('account', username=username))
    else:
        flash('User {} not found.'.format(username))
        return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in', 'info')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')

            return redirect(next_page)
        else:
            flash('Invalid username or password !!' , 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()