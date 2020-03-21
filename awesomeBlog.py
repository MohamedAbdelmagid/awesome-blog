import os

from webapp import create_app, db
from webapp.models import User, Post
from webapp.translation import translate_with_microsoft, translate_with_google, translate_sentence


sentenceToTranslate = "Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991, Python's design philosophy emphasizes code readability with its notable use of significant whitespace. Its language constructs and object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects."

app = create_app(os.environ.get('APP_SETTINGS'))

users = User.query.all()
posts = Post.query.all()

def allusers():
    for user in users:
        print(user)
    
def allposts():
    for post in posts:
        print(post)

def get(id):
    return User.query.get(id)

def getPost(id):
    return Post.query.get(id)

def deletePost(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return 'deleted !!'

def deleteUser(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return 'deleted !!'

def deletePosts(id):
    posts = Post.query.all()
    for post in posts:
        db.session.delete(post)
    db.session.commit()
    
    return 'All posts have been deleted !!!'

def deleteUsers(id):
    users = User.query.all()
    for user in users:
        db.session.delete(user)
    db.session.commit()

    return 'All users have been deleted !!!'

# This funtion get all posts written by a paticular user 
def getPosts(id):
    posts = Post.query.filter_by(user_id=id)
    for post in posts:
        print(post)
    return list(posts)

# Some command for working with the shell 
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'users': users,
        'posts': posts,
        'allusers': allusers,
        'allposts': allposts,
        'get': get, # get the user with this id
        'getPost': getPost,
        'getPosts': getPosts,
        'deleteUser': deleteUser,
        'deleteUsers': deleteUsers,
        'deletePost': deletePost,
        'deletePosts': deletePosts,
        'soft': translate_with_microsoft,
        'google': translate_with_google,
        'tran': translate_sentence,
        'sen': sentenceToTranslate
    }


if __name__ == '__main__':
    app.run()