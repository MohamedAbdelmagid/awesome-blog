from werkzeug.urls import url_parse

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from webapp import app, db
from webapp.models import User
from webapp.utils import store_image
from webapp.forms import LoginForm, RegistrationForm, UpdateProfileForm


@app.route('/')
@app.route('/home')
@login_required
def home():
    user = {'username': 'Mohamed Abdelmagid'}
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
    return render_template('home.html', title='Home Page', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            image_file = store_image(form.picture.data)
            current_user.image_file = image_file
             
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your profile has been updated !', 'info')
        return redirect(url_for('profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('profile.html', title='Profile', image_file=image_file, form=form)


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