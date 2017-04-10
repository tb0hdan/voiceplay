#-*- coding: utf-8 -*-
""" Local library playback module """

import os
import random
random.seed()
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class LocalLibrary(APIV1Resource):
    """
    Local file library API endpoint
    """
    route_base = '/api/v1/play/locallibrary'
    queue = None
    def post(self):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play my library')
            result = {'status': 'ok', 'message': message}
        return result


class LocalLibraryTask(BasePlayerTask):
    """
    Local library playback class
    Uses hardcoded path
    """
    __group__ = ['play', 'shuffle']
    __regexp__ = ['^play (.+)?my library$', '^shuffle (.+)?my library$']
    __priority__ = 50

    @classmethod
    def play_local_library(cls):
        """
        Very basic local library shuffler
        """
        fnames = []
        library = os.path.expanduser('~/Music')
        for root, _, files in os.walk(library, topdown=False):
            for name in files:
                if name.lower().endswith('.mp3'):
                    fnames.append(os.path.join(root, name))
        random.shuffle(fnames)
        for fname in fnames:
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play(fname, fname.rstrip('.mp3'))

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        cls.say('Shuffling songs in local library')
        cls.play_local_library()
