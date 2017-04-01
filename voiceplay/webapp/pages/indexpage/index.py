import time
from flask import render_template
from flask_classy import FlaskView, route

class IndexView(FlaskView):
    route_base = '/'

    @route('/')
    @route('/index.html')
    def index(self):  # pylint:disable=no-self-use
        timestamp = int(time.time())
        return render_template('my_index.html', timestamp=timestamp)
