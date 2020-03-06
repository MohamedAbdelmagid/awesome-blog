from webapp import app, db
from webapp.models import User, Post


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
    }


if __name__ == '__main__':
    app.run()