#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest

from webapp import create_app, db
from webapp.models import User, Post

from config import TestingConfig


class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='wamda')
        u.set_password('password')
        self.assertFalse(u.check_password('wrongPassword'))
        self.assertTrue(u.check_password('password'))

    def test_follow(self):
        mohamed = User(username='mohamed', email='mohamed@test.com')
        wamda = User(username='wamda', email='wamda@test.com')
        db.session.add(mohamed)
        db.session.add(wamda)
        db.session.commit()
        self.assertEqual(mohamed.followed.all(), [])
        self.assertEqual(mohamed.followers.all(), [])

        mohamed.follow(wamda)
        db.session.commit()
        self.assertTrue(mohamed.is_following(wamda))
        self.assertEqual(mohamed.followed.count(), 1)
        self.assertEqual(mohamed.followed.first().username, 'wamda')
        self.assertEqual(wamda.followers.count(), 1)
        self.assertEqual(wamda.followers.first().username, 'mohamed')

        mohamed.unfollow(wamda)
        db.session.commit()
        self.assertFalse(mohamed.is_following(wamda))
        self.assertEqual(mohamed.followed.count(), 0)
        self.assertEqual(wamda.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        mohamed = User(username='mohamed', email='mohamed@test.com')
        wamda = User(username='wamda', email='wamda@test.com')
        ragda = User(username='ragda', email='ragda@test.com')
        abdeen = User(username='abdeen', email='abdeen@test.com')
        db.session.add_all([mohamed, wamda, ragda, abdeen])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(title="Mohamed post's title", content="post from mohamed", author=mohamed,
                  date_posted=now + timedelta(seconds=1))
        p2 = Post(title="Wamda post's title", content="post from wamda", author=wamda,
                  date_posted=now + timedelta(seconds=4))
        p3 = Post(title="Ragda post's title", content="post from ragda", author=ragda,
                  date_posted=now + timedelta(seconds=3))
        p4 = Post(title="Abdeen post's title", content="post from abdeen", author=abdeen,
                  date_posted=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])    
        db.session.commit()

        # setup the followers
        mohamed.follow(wamda)  # mohamed follows wamda
        mohamed.follow(abdeen)  # mohamed follows abdeen
        wamda.follow(ragda)  # wamda follows ragda
        ragda.follow(abdeen)  # ragda follows abdeen
        db.session.commit()

        # check the followed posts of each user
        f1 = mohamed.followed_posts().all()
        f2 = wamda.followed_posts().all()
        f3 = ragda.followed_posts().all()
        f4 = abdeen.followed_posts().all()
        self.assertEqual(f1, [p2, p4])
        self.assertEqual(f2, [p3])
        self.assertEqual(f3, [p4])
        self.assertEqual(f4, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)