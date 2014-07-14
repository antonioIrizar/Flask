from flask import Flask
from flask.ext.admin import Admin, BaseView, expose

class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')

    #def is_accessible(self):
     #   return login.current_user.is_authenticated()

app = Flask(__name__)

admin = Admin(name = 'My first App')

# Add administrative views here
# Add views here
admin.init_app(app)
# admin.add_view(MyView(name='Hello'))
admin.add_view(MyView(name='Hello 1', endpoint='test1', category='Test'))
admin.add_view(MyView(name='Hello 2', endpoint='test2', category='Test'))
admin.add_view(MyView(name='Hello 3', endpoint='test3', category='Test'))
app.run(debug=True)
