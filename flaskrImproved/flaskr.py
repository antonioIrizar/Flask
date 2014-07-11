# imports. we can put in oder file. the name of file in this case is .ini or .py
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskrImproved.db'),
    #only in developer environment
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# use this command to initialize database: sqlite3 /tmp/flaskrImproved.db < schema.sql
# and in python sell, we use the next two command:
#from flaskr import init_db
#init_db()
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    #querying to sqllite3
    cur = db.execute('select title, text from entries order by id desc')
    #Fetches all rows of a query result, returning a list
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #request.form['username'] need be in []
        user = query_db('select * from users where user = ?',[request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif user['pass'] != request.form['password']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/register', methods=['GET','POST'])
def register():
    error=None
    if request.method == 'POST':
        user = query_db('select * from users where user = ?',[request.form['username']], one=True)
        if user is None:
            db = get_db()
            db.execute('insert into users (user, pass) values (?, ?)',[request.form['username'], request.form['password']])
            db.commit()
            flash('You create a new accont')
            return redirect(url_for('show_entries'))
        else:
            error = 'Username in use. Take other username please'
    return render_template('register.html', error=error)

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

if __name__ == '__main__':
    app.run()