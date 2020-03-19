from datetime import datetime
from werkzeug.urls import url_parse

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from guess_language import guess_language

from webapp import app, db
from webapp.models import User, Post
from webapp.utils import store_image, send_password_reset_email, translate, translate_with_google
from webapp.forms import LoginForm, RegistrationForm, UpdateProfileForm, PostForm, ResetPasswordForm, ResetPasswordRequestForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.content.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''

        post = Post(title=form.title.data, content=form.content.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()

        flash('Your post is now live!')
        return redirect(url_for('home'))

    page = request.args.get('page', 1, type=int)
    followed_posts = current_user.followed_posts()
    posts = followed_posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('home', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('home', page=posts.prev_num) if posts.has_prev else None

    displayPagination = followed_posts.count() > app.config['POSTS_PER_PAGE']

    return render_template('home.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, display=displayPagination)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    all_posts = Post.query.order_by(Post.date_posted.desc())
    posts = all_posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None

    displayPagination = all_posts.count() > app.config['POSTS_PER_PAGE']

    return render_template("home.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url, display=displayPagination)


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
    posts = user.posts.order_by(Post.date_posted.desc()).all()

    image_file = url_for('static', filename='pics/' + user.image_file)

    return render_template('account.html', user=user, image_file=image_file, posts=posts, articles=len(posts))

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


@app.route('/reset_password/<token>', methods=['GET', 'POST'])  
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)

        db.session.commit()
        flash('Your password has been reset.')

        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
        
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    text = request.form['text']
    source_language = request.form['source_language']
    dest_language = request.form['dest_language']
    
    translatedText = translate(text, source_language, dest_language)
    if 'ArgumentException' in translatedText or 'Exception' in translatedText:
        # We could use translate_with_google if there is a problem with Microsoft API
        translatedText = translate_with_google(text, source_language, dest_language)
    
    return jsonify({'text': translatedText})