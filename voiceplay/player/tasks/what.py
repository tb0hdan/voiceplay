#-*- coding: utf-8 -*-
""" Interaction task module """


import re
import time
from voiceplay.logger import logger
#from voiceplay.webapp.baseresource import APIV1Resource
from .basetask import BasePlayerTask


class WhatTask(BasePlayerTask):
    """
    This task doesn't play anything, just provides info
    """
    __group__ = ['what']
    __regexp__ = ['^what are top albums (?:by|for) (.+)$',
                  '^what are top (?:songs|tracks) (?:by|for) (.+)$',
                  '^what time(.+)$', '^what (?:date|day)(.+)$',
                  '^(?:date|day)(.+)$']
    __priority__ = 100

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        artist = re.match(regexp, message, re.I).groups()[0]
        if 'albums' in regexp:
            albums = cls.lfm().get_top_albums(artist)
            msg = cls.lfm().numerize(albums[:10])
            logger.warning('Here are top albums by %s - %s', artist, msg)
            cls.say('Here are top albums by %s - %s' % (artist, msg))
        elif 'songs' in regexp or 'tracks' in regexp:
            tracks = cls.lfm().get_top_tracks(artist)[:10]
            numerized = ', '.join(cls.lfm().numerize(tracks))
            reply = re.sub(r'^(.+)\.\s\d\:\s', '1: ', numerized)
            logger.warning('Here are some top tracks by %s: %s', artist, reply)
            cls.say('Here are some top tracks by %s: %s' % (artist, reply))
        elif 'time' in regexp:
            cls.say('It is %s %s right now' % (int(time.strftime('%H')), int(time.strftime('%M'))))
        elif 'date' in regexp or 'day' in regexp:
            weekday = time.strftime('%A')
            month_name = time.strftime('%B')
            daynum = int(time.strftime('%d'))
            cls.say('It is %s %s %s' % (weekday, month_name, daynum))
