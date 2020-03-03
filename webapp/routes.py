from flask import render_template
from webapp import app


@app.route('/')
@app.route('/home')
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
    return render_template('home.html', user=user, posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

