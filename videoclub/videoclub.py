import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import Admin, expose, helpers
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

"""class MyAdmin(admin.AdminIndexView):
    
    def is_visible(self):
        if if not session.get('logged_in'):
            return False
        return True
"""
#class MyAdminExpose(MyAdmin):
class MyAdminExpose(admin.AdminIndexView):
    """    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return self.render("videoclub_admin/index.html")
        return self.render("videoclub_admin/index.html")
    """
    @expose('/')
    def index(self):
        #if not self.is_accessible():
        if not session.get('logged_in'):
            return  redirect(url_for('.login'))
        return self.render("videoclub_admin/index.html")
        #super(MyAdmin, self).index()
#if not login.current_user.is_authenticated():
#           return redirect(url_for('.login_view'))
    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        #self.render("micarpeta/miplantilla.html", form = form)
        form = LoginForm(request.form)
        if form.validate_on_submit():
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('.index'))
        #self._template_args['form'] = form
        return self.render("videoclub_admin/index.html", form = form)
        #super(MyAdmin, self).index()

    @expose('/logout/')
    def logout(self):
        session.pop('logged_in', None)
        flash('You were logged out')
        return redirect(url_for('.login'))

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

    def is_visible(self):
        if not session.get('logged_in'):
            return False
        return True

    column_display_pk = True
    form_columns = ['name', 'year', 'description', 'totalNumber', 'numberAvailable']


class LoginForm(Form):

    username = TextField("Username")
    password = PasswordField("Password")
    submit = SubmitField("Login")

    def validate_user(self,field):
        
        user = db.session.query(User).filter_by(name=self.username, password = self.password).first()
        if user is None:
            raise ValidationError("Invalid user")



# Create admin
#admin = admin.Admin(app, 'Videoclub', index_view=BaseView())
admin = admin.Admin(app, 'Videoclub', index_view=MyAdminExpose(), base_template='videoclub_admin/myMaster.html')
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