#-*- coding: utf-8 -*-
""" URL playback task module (with some pixie dust)"""

import logging
import re

from youtube_dl import YoutubeDL

from voiceplay.logger import logger
from .basetask import BasePlayerTask

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
    new_description = None

    @classmethod
    def url_hook(cls, *args, **kwargs):
        message = args[0]
        if message.startswith('http'):
            cls.new_url = message
        elif message.startswith('['):
            logger.debug(message)
        else:
            cls.new_description = message

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        url = re.match(regexp, message).groups()[0]
        cls.say('Playing music from url')
        verbose = logger.level == logging.DEBUG
        ydl_opts = {'verbose': verbose, 'quiet': not verbose, 'forceurl': True, 'forcetitle': True,
                    'logger': logger, 'simulate': True, 'noplaylist': True}
        logger.debug('Using source url %s', url)
        YoutubeDL.to_stdout = cls.url_hook
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        description = url
        if cls.new_url and cls.new_url != url:
            url = cls.new_url
            description = cls.new_description if cls.new_description else url
        cls.play_url(url, description)
