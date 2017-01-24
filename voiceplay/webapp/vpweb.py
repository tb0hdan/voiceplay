import multiprocessing

import gunicorn.app.base
from gunicorn.six import iteritems

from flask import Flask, request
from flask_classy import FlaskView
from flask_restful import Resource, Api


class IndexView(FlaskView):
    def index(self):
        return 'Hello'


class Artist(Resource):
    queue = None
    def get(self, artist, query):
        if self.queue and artist and query:
            self.queue.put('play' + ' %s ' % query + ' by ' + artist)
        return {'status': 'ok'}

class Album(Resource):
    queue = None
    def get(self, artist, album):
        if self.queue and artist and album:
            self.queue.put('play tracks from' + ' %s ' % album + ' by ' + artist)
        return {'status': 'ok'}


class Station(Resource):
    queue = None
    def get(self, station):
        if self.queue and station:
            self.queue.put('play' + ' %s ' % station + 'station')
        return {'status': 'ok'}


class WebApp(object):
    def __init__(self, port=8000, queue=None):
        self._debug = False
        self._app = Flask(__name__)
        self.api = Api(self._app)
        self.port = port
        self.queue = queue

    @property
    def app(self):
        return self._app

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value

    def register(self):
        # TODO: Move this to plugins
        Artist.queue = self.queue
        self.api.add_resource(Artist, '/api/v1/play/artist/<artist>/<query>')
        #
        Album.queue = self.queue
        self.api.add_resource(Album, '/api/v1/play/artist/<artist>/album/<album>')
        #
        Station.queue = self.queue
        self.api.add_resource(Station, '/api/v1/play/station/<station>')
        #
        IndexView.register(self._app, route_base='/')

    def run(self):
        self._app.run(debug=self._debug, port=self.port)


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """
    """
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class WrapperApplication(object):
    def __init__(self, mode='local', port=8000):
        self.mode = mode
        self.port = port

    def run(self, queue=None):
        webapp = WebApp(port=self.port, queue=queue)
        webapp.register()
        if self.mode == 'local':
            webapp.debug = True
            webapp.run()
        elif self.mode == 'prod':
            options = {
                'bind': '%s:%s' % ('127.0.0.1', str(self.port)),
                'workers': (multiprocessing.cpu_count() * 2) + 1,
            }
            StandaloneApplication(webapp.app, options).run()


if __name__ == '__main__':
    wa = WrapperApplication(mode='prod')
    wa.run()
