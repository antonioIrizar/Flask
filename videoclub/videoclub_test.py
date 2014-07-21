import os
import videoclub
from videoclub import db,Flask,User
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

	def setUp(self):
		self.app=Flask(__name__)
		db.init_app(self.app)
		with self.app.app_context():
			db.drop_all()
			db.create_all()
			test_user = User(name="test", password="test")
			db.session.add(test_user)
			db.session.commit()

	def tearDown(self):
		self.app = Flask(__name__)
		db.init_app(self.app)
		with self.app.app_context():
			db.drop_all()

	def login(self,username,password):
		return self.app.post('/login/', data=dict(username=username,password=password), follow_redirects=True)

	def logout(self):
		return self.app.get('/admin/logout/', follow_redirects=True)

	def test_login_logout(self):
		rv = self.login(videoclub.app.config['username'],
                        videoclub.app.config['password'])
		assert 'You were logged in' in rv.data
		rv = self.logout()
		assert 'You were logged out' in rv.data

if __name__ == '__main__':
		unittest.main()