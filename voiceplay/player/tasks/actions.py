#-*- coding: utf-8 -*-
""" Track actions task module """

from voiceplay.database import voiceplaydb
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class CurrentTrackResource(APIV1Resource):
    """
    Current track API endpoint
    """
    route_base = '/api/v1/tracks/current'
    queue = None
    def get(self):
        """
        HTTP GET handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('current_track')
            result = {'status': 'ok', 'message': message}
        return result

class LoveTrackResource(APIV1Resource):
    """
    Love track API endpoint
    """
    route_base = '/api/v1/tracks/love'
    queue = None
    def get(self):
        """
        HTTP GET handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('love')
            result = {'status': 'ok', 'message': message}
        return result

class BanTrackResource(APIV1Resource):
    """
    Ban track API endpoint
    """
    route_base = '/api/v1/tracks/ban'
    queue = None
    def get(self):
        """
        HTTP GET handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('ban')
            result = {'status': 'ok', 'message': message}
        return result


class CurrentTrackTask(BasePlayerTask):
    """
    Get current track
    """
    __group__ = ['current_track']
    __regexp__ = ['^current(.+)?$']
    __priority__ = 190

    @classmethod
    def process(cls, regexp, message):
        """
        Run task - get current track
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        current_track = cls.get_current_track()
        cls.say('Current track is %s' % current_track)
        return current_track

class LoveTrackTask(BasePlayerTask):
    """
    Love current track
    """
    __group__ = ['love', 'like', 'unban']
    __regexp__ = ['^love(.+)?$', '^like(.+)?$', '^unban(.+)?$']
    __priority__ = 210

    @classmethod
    def process(cls, regexp, message):
        """
        Run task - get current track and set status to 'love'
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        current_track = cls.get_current_track()
        if current_track:
            voiceplaydb.set_track_status(current_track, 'loved')
            cls.say('Track %s was marked as loved' % current_track)
        return None

class BanTrackTask(BasePlayerTask):
    """
    Ban current track
    """
    __group__ = ['ban', 'hate', 'dislike']
    __regexp__ = ['^ban(.+)?$', '^hate(.+)?$', '^dislike(.+)?$']
    __priority__ = 220

    @classmethod
    def process(cls, regexp, message):
        """
        Run task - get current track and set status to 'ban'
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        current_track = cls.get_current_track()
        if current_track:
            voiceplaydb.set_track_status(current_track, 'banned')
            cls.say('Track %s was marked as banned' % current_track)
        return None
