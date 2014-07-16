import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import Admin, BaseView, expose
from sqlalchemy import UniqueConstraint

# Create application
app = Flask(__name__)


# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')

#if not login.current_user.is_authenticated():
#           return redirect(url_for('.login_view'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #request.form['username'] need be in []
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(User).filter_by(name=username, password = password).first()
       
        if user is None:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for("admin.index"))            
    return render_template('login.html', error=error)



class Movie(db.Model):
    __tablename__ = 'Movie'
    name = db.Column(db.String(50), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150))
    totalNumber = db.Column(db.Integer)
    numberAvailable = db.Column(db.Integer)

    #__table_args__ = (UniqueConstraint('name', 'year',name= 'das'),)

    def __unicode__(self):
        return self.name

class User (db.Model):
	__tablename__ = 'User'
	name = db.Column(db.String(50),primary_key = True, unique=True)
	password = db.Column(db.String(20))

	def  __repr__(self):
		return '%s','%s' % (self.name,self.password)

	def __unicode__(self):
		 print '%s - %s' % (self.name, self.password)



class MovieAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['name', 'year', 'description', 'totalNumber', 'numberAvailable']



# Create admin
#admin = admin.Admin(app, 'Videoclub', index_view=BaseView())
admin = admin.Admin(app, 'Videoclub')
admin.add_view(MovieAdmin(Movie, db.session))
#admin.add_view(TyreAdmin(Tyre, db.session))

if __name__ == '__main__':    

    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    #if not os.path.exists(database_path):
        # Create DB
    db.drop_all()
    db.create_all()
    test_user = User(name="test", password="test")
    db.session.add(test_user)

    db.session.commit()
    # Start app
    app.run(debug=True)