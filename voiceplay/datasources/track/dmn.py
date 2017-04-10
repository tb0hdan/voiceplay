#-*- coding: utf-8 -*-
""" DailyMotion track source module """
from __future__ import division

from math import trunc

from dailymotion import Dailymotion

from .basesource import TrackSource

class DailyMotionSource(TrackSource):
    """
    DailyMotion track source
    """
    __baseurl__ = 'http://www.dailymotion.com/video/'
    __priority__ = 30

    @classmethod
    def search(cls, query, max_results=25):
        """
        Run dailymotion search
        """
        maxresults = 100
        client = Dailymotion()
        results = []
        pages = trunc(max_results/maxresults)
        pages = pages if pages > 0 else 1
        dquery = {'search': query,
                  'fields':'id,title',
                  'limit': maxresults}
        i = 0
        while i < pages:
            response = client.get('/videos', dquery)
            results += response.get('list', [])
            i += 1
            if not response.get('has_more', False):
                break
        videos = []
        for result in results:
            vid = result.get('id')
            title = result.get('title')
            if not title.lower().startswith(query.lower()):
                continue
            videos.append([title, vid])
        return videos
