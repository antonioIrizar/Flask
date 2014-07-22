import os
import videoclub
from videoclub import db,Flask,User,app
import unittest
import tempfile

class VideoclubTestCase(unittest.TestCase):
    """
    def setUp(self):
        #self.app=Flask(__name__)
        #db.init_app()
        with app.app_context():
            db.drop_all()
            db.create_all()
            test_user = User(name="test", password="test")
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        #self.app = Flask(__name__)
        #db.init_app(self.app)
        with app.app_context():
            db.drop_all()
    """
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['DATABASE_FILE'] = 'test.sqlite'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
        self.app = app.test_client()
        db.create_all()
        test_user = User(name="test", password="test")
        db.session.add(test_user)
        db.session.commit()


    def tearDown(self):
        db.drop_all()

    """
    def setUp(self):
        self.db_fd, videoclub.app.config['DATABASE'] = tempfile.mkstemp()
        videoclub.app.config['TESTING'] = True
        self.app = videoclub.app.test_client()
        videoclub.db.create_all

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(videoclub.app.config['DATABASE'])

    """
    def login(self,username,password):
        return app.post('/admin/login/', data=dict(username=username,password=password), follow_redirects=True)

    def logout(self):
        return app.get('/admin/logout/', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('test',
                        'test')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data

if __name__ == '__main__':
        unittest.main()
