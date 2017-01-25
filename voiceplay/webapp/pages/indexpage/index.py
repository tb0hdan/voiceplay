from flask import render_template
from flask_classy import FlaskView

class IndexView(FlaskView):
    route = '/'
    def index(self):
        return render_template('my_index.html')
