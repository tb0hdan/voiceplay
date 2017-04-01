import time
from flask import render_template
from flask_classy import FlaskView, route

class IndexView(FlaskView):
    route_base = '/'

    @route('/')
    @route('/index.html')
    @staticmethod
    def index():
        timestamp = int(time.time())
        return render_template('my_index.html', timestamp=timestamp)
