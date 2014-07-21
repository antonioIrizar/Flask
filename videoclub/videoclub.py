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
from datetime import date
from flask.ext.admin.actions import action
from flask.ext.babel import Babel
from flask.ext.babel import gettext, ngettext

# Create application
app = Flask(__name__)

babel = Babel(app)
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = False
app.config.from_pyfile('babel.cfg')
db = SQLAlchemy(app)


# available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Espanol'
}


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

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
            flash(gettext(u'You were logged in'))
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


listUserMyMovie = db.Table('listUserMyMovie',
    db.Column('myMovie_id', db.Integer, db.ForeignKey('myMovie.id')),
    db.Column('user_name', db.String(50), db.ForeignKey('user.name'))
    #column('movie_year',String,ForeignKey('movie.year'))
 )

listMovies = db.Table('listMovies',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('myMovie_id', db.Integer, db.ForeignKey('myMovie.id'))
    #column('movie_year',String,ForeignKey('movie.year'))
 )

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50),nullable=False )
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(150))
    totalNumber = db.Column(db.Integer, nullable=False)
    numberAvailable = db.Column(db.Integer, nullable=False)

    __table_args__ = (UniqueConstraint('name', 'year'),)

    def __unicode__(self):
        return self.name

    def  __repr__(self):
        return '%s' % (self.name)

class User (db.Model):
	__tablename__ = 'user'
	name = db.Column(db.String(50),primary_key = True, unique=True)
	password = db.Column(db.String(20))

	def  __repr__(self):
		return '%s' % (self.name)

	def __unicode__(self):
		 print '%s - %s' % (self.name, self.password)

class MyMovie (db.Model):
    __tablename__ = 'myMovie'
    id = (db.Column(db.Integer,primary_key=True))
    catch = db.Column(db.Date)
    giveBack = db.Column(db.Date)

    user = db.relationship('User', secondary = listUserMyMovie, backref = 'myMovie')
    movie = db.relationship('Movie', secondary = listMovies, backref = 'myMovie')

    def __unicode__(self):
        print '%s - %s' % (self.catch, self.giveBack)

    def  __repr__(self):
        return '%s','%s' % (self.catch,self.giveBack)



class ViewModelAdmin(sqla.ModelView):
    def is_accessible(self):
        if not session.get('logged_in'):
            return False
        return True

    def is_visible(self):
        if not session.get('logged_in'):
            return False
        return True

    def _handle_view(self, name, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin.login')) 
        

#view of movies to admin
class MovieAdmin(ViewModelAdmin):
    
    column_display_pk = True
    form_columns = ['name', 'year', 'description', 'totalNumber', 'numberAvailable']

    @action('Take Movie','Rent',
            'do you want rent the select movie?')
    def action_prueba(self, ids):
        #query = get_query_for_ids(self.get_query(), self.model, ids)
        count = 0

        #for m in query.all():
         #   m.update({"numberAvailable": 1 })
         #   count += 1

        #self.session.commit()

        #flash(ngettext('Model was successfully deleted.','%(count)s models were successfully deleted.',count,count=count))
        for i in ids:
            print i
            movie= db.session.query(Movie).filter_by(id=i).first()
            if movie.numberAvailable == 0:
                flash("Error one or more movies not available")
                db.session.rollback()
                return
            else: 
                db.session.query(self.model).filter_by(id=i).update({"numberAvailable" : movie.numberAvailable-1})
                today = date.today()
                if today.day == 30 :
                    myMovie = MyMovie(catch = today, giveBack = date(today.year,today.month,1))
                else:
                    myMovie = MyMovie(catch = today, giveBack = date(today.year,today.month,31))
                db.session.add(myMovie)
                myMovie.user.append(db.session.query(User).filter_by(name = session.get('user')).first())
                myMovie.movie.append(movie)
                #duda por que esta linea no vale porque modifica los dos
                #numberAvailable.query.update({"numberAvailable" : numberAvailable.numberAvailable-1})
                
        db.session.commit()
        
        flash("You rent de movie")
        #print "tarara"


#class to WTF-form

class MyListMovies(ViewModelAdmin):

    @expose('/')
    def index(self):
        #preguntar si se puede acceder desde los templates al resto de atributos de las relaciones many to many es decir algo asi  ejemplo:movie.movie.id 
        myMovies = db.session.query(MyMovie).filter(MyMovie.user.any(name=session.get('user'))).all()
        return self.render('videoclub_admin/myMovies.html', myMovies = myMovies)
 

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
admin.add_view(MyListMovies(MyMovie, db.session))

if __name__ == '__main__':    

    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    #if not os.path.exists(database_path):
        # Create DB
    db.drop_all()
    db.create_all()
    test_user = User(name="test", password="test")
    movie = Movie(name = "peli1", year = 2014,totalNumber= 1 ,numberAvailable= 1)
    movie2 = Movie(name = "peli2", year = 2014, totalNumber = 14 ,numberAvailable=0)
    db.session.add(movie)
    db.session.add(movie2)
    db.session.add(test_user)
    today = date.today()
    if today.day == 30:
        myMovie = MyMovie(catch = today, giveBack = date(today.year,today.month,1))
        myMovie2 = MyMovie(catch = today, giveBack = date(today.year,today.month,1))
    else:
        myMovie = MyMovie(catch = today, giveBack = date(today.year,today.month,today.day+1))
        myMovie2 = MyMovie(catch = today, giveBack = date(today.year,today.month,today.day+1))
    db.session.add(myMovie)
    myMovie.user.append(test_user)
    myMovie.movie.append(movie)
    
    db.session.add(myMovie2)
    myMovie2.movie.append(movie2)
    myMovie2.user.append(test_user)

    db.session.commit()

    # Start app
    app.run(debug=True)