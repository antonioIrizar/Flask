from flask.ext.testing import TestCase

from videoclub import create_app, db

class MyTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"+"test.sqlite"
    TESTING = True

    def create_app(self):

        # pass in test configuration
        return create_app(self)

    def setUp(self):

        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()