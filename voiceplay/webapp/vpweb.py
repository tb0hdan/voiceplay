#-*- coding: utf-8 -*-
""" Voiceplay Web API module """

import multiprocessing

import gunicorn.app.base
from gunicorn.six import iteritems

from flask import Flask
from flask_classy import FlaskView
from flask_restful import Api


from voiceplay.config import Config
from voiceplay.utils.loader import PluginLoader

from .baseresource import APIV1Resource


class WebApp(object):
    def __init__(self, port=None, queue=None):
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
        # Register resources
        resources = sorted(PluginLoader().find_classes('voiceplay.player.tasks', APIV1Resource))
        resources += sorted(PluginLoader().find_classes('voiceplay.player.controls', APIV1Resource))
        for resource in resources:
            resource.queue = self.queue
            self.api.add_resource(resource, resource.route_base)
        # Register pages
        pages = sorted(PluginLoader().find_classes('voiceplay.webapp.pages', FlaskView))
        for page in pages:
            # same as above for resources
            page.register(self._app, route_base=page.route_base)

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
    def __init__(self, mode='prod', port=None):
        self.mode = mode
        self.port = port if port else int(Config.cfg_data().get('webapp_port'))
        self._debug = False

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value

    def run(self, queue=None):
        webapp = WebApp(port=self.port, queue=queue)
        webapp.register()
        if self.mode == 'local':
            # hardcore debugging only
            webapp.debug = self.debug
            webapp.run()
        elif self.mode == 'prod':
            options = {
                'bind': '%s:%s' % ('0.0.0.0', str(self.port)),
                'workers': (multiprocessing.cpu_count() * 2) + 1,
                'capture_output': True,
                'loglevel': 'debug' if self.debug else 'info'
            }
            StandaloneApplication(webapp.app, options).run()
