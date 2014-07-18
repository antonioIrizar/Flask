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
from sqlalchemy.exc import IntegrityError

# Create application
app = Flask(__name__)


# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
#app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


#views of page
class MyAdminExpose(admin.AdminIndexView):

    @expose('/')
    def index(self):

        if not session.get('logged_in'):
            return  redirect(url_for('.login'))
        return self.render("videoclub_admin/index.html")

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        error = None
        form = LoginForm(request.form)
        if form.validate_on_submit():
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('.index'))
        error = 'the username or password are wrong'
        flash('The username or password are wrong')
        return self.render("videoclub_admin/index.html", form = form, error=error)

    @expose('/logout/')
    def logout(self):
        session.pop('logged_in', None)
        session.pop('user',None)
        flash('You were logged out')
        return redirect(url_for('.login'))

    @expose('/register/', methods=['GET','POST'])
    def register(self):
        form = RegisterForm(request.form)
        if form.validate_on_submit():
            user = User()
            user.name = form.username.data
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash("New user create.")
            return redirect(url_for('.login'))
        flash ("error in creation new user")
        return self.render("videoclub_admin/register.html", form = form)

#Models of database

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


class ViewModelAdmin(sqla.ModelView):
    def is_accessible(self):
        if not session.get('logged_in'):
            return False
        return True

    def is_visible(self):
        if not session.get('logged_in'):
            return False
        return True
        

#view of movies to admin
class MovieAdmin(ViewModelAdmin):

    def _handle_view(self, name, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin.login')) 

    def handle_view_exception(self, exc):
        if isinstance(exc, IntegrityError):
            #flash(gettext('Integrity error. %(message)s', message=exc.message), 'error')
            flash('Integrity error')
            return True

        return super(ModelView, self).handle_view_exception(exc)

    def create_model(self, form):
        """
Create model from form.

:param form:
Form instance
        """
        try:
            model = self.model()
            form.populate_obj(model)
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to create model. %(error)s', error=str(ex)), 'error')
                log.exception('Failed to create model')

            self.session.rollback()

            return False
        else:
            self.after_model_change(form, model, True)

        return True


    
    column_display_pk = True
    form_columns = ['name', 'year', 'description', 'totalNumber', 'numberAvailable']


#class to WTF-form

class LoginForm(Form):

    username = TextField("Username")
    password = PasswordField("Password")
    submit = SubmitField("Login")

    def validate_username(self,field):
        user = db.session.query(User).filter_by(name=field.data, password = self.password.data).first()
        session['user'] = field.data
        if user is None:
            raise ValidationError("Invalid user")

class  RegisterForm(Form):
    username = TextField("Username")
    password = PasswordField("Password")
    submit = SubmitField("Register")

    def validate_username(self,field):
        user = db.session.query(User).filter_by(name=field.data).first()
        if user is not None:
            raise ValidationError("Username in use take othres please ")
        



# Create admin
admin = admin.Admin(app, 'Videoclub', index_view=MyAdminExpose(), base_template='videoclub_admin/myMaster.html')
admin.add_view(MovieAdmin(Movie, db.session))

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