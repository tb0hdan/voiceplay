#-*- coding: utf-8 -*-
""" URL playback task module (with some pixie dust)"""

import logging
import re

from flask import request
from youtube_dl import YoutubeDL

from voiceplay.logger import logger
from voiceplay.webapp.baseresource import APIV1Resource
from .basetask import BasePlayerTask


class URLPlaybackResource(APIV1Resource):
    route = '/api/v1/play/url'
    queue = None
    def post(self):
        if self.queue and request.form['data']:
            url = request.form['data']
            self.queue.put('play url' + ' %s ' % url)
        return {'status': 'ok'}


class URLTask(BasePlayerTask):
    """
    URL playback task
    Support for: play url http://domain
    """
    __group__ = ['play']
    __regexp__ = ['^play url (.+)$']
    __priority__ = 140
    __actiontype__ = 'url_task'

    new_url = None
    title = None
    tracklist = []

    @classmethod
    def add_to_list(cls):
        if cls.title and cls.new_url:
            cls.tracklist.append([cls.new_url, cls.title])
            cls.title = None
            cls.new_url = None

    @classmethod
    def url_hook(cls, *args, **kwargs):
        message = args[0]
        if not message.startswith('http') and not message.startswith('['):
            cls.add_to_list()
            cls.title = message
        elif message.startswith('http'):
            cls.add_to_list()
            cls.new_url = message
        else:
            logger.debug(message)

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        # reset vars
        cls.new_url = None
        cls.title = None
        cls.tracklist = []
        #
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        url = re.match(regexp, message, re.I).groups()[0]
        cls.say('Playing music from url')
        verbose = logger.level == logging.DEBUG
        ydl_opts = {'verbose': verbose, 'quiet': not verbose, 'forceurl': True, 'forcetitle': True,
                    'logger': logger, 'simulate': True, 'noplaylist': False, 'ignoreerrors': True}
        logger.debug('Using source url %s', url)
        YoutubeDL.to_stdout = cls.url_hook
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if not cls.tracklist:
            cls.tracklist.append([url, url])
        for url, description in cls.tracklist:
            cls.play_url(url, description)
