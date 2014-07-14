from sqla import app
from sqla.database import db_session

@app.route('/')
def index():
    return 'Hello World!'

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

