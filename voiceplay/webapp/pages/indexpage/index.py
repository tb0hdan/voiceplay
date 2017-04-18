#-*- coding: utf-8 -*-
""" Index page module """

import time
from flask import render_template
from flask_classy import FlaskView, route

class IndexView(FlaskView):
    """
    Flask View for index page
    """
    route_base = '/'

    @route('/')
    @route('/index.html')
    def index(self):  # pylint:disable=no-self-use
        """
        Index page renderer
        """
        timestamp = int(time.time())
        return render_template('my_index.html', timestamp=timestamp)
