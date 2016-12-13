#-*- coding: utf-8 -*-

import re

from voiceplay.logger import logger
from .basetask import BasePlayerTask

class URLTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = ['^play url (.+)$']
    __priority__ = 130
    __actiontype__ = 'url_task'

    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        url = re.match(regexp, message).groups()[0]
        cls.say('Playing music from url')
        cls.play_url(url, url)
