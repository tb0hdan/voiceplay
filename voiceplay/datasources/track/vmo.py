#-*- coding: utf-8 -*-
""" Vimeo track source module """

import json
import sys

from future.standard_library import install_aliases
install_aliases()

from urllib.parse import quote

import vimeo
from .basesource import TrackSource


class VimeoSource(TrackSource):
    """
    Vimeo track source
    """
    __baseurl__ = 'https://vimeo.com/'
    __priority__ = 20

    @classmethod
    def search(cls, query, max_results=25):
        """
        Run vimeo search
        """
        if sys.version_info.major == 2:
            CHECK = unicode
        elif sys.version_info.major == 3:
            CHECK = str
        if isinstance(query, CHECK) and sys.version_info.major == 2:
            query = query.encode('utf-8')
        client = vimeo.VimeoClient(token=cls.cfg_data()['vimeo']['token'],
                                   key=cls.cfg_data()['vimeo']['key'],
                                   secret=cls.cfg_data()['vimeo']['secret'])
        response = client.get('/videos?query=%s' % quote(query))
        result = json.loads(response.text).get('data', [])
        videos = []
        for video in result:
            vid = video.get('uri', '').split('/videos/')[1]
            title = video.get('name', '')
            if not title.lower().startswith(query.lower()):
                continue
            videos.append([title, vid])
        return videos
