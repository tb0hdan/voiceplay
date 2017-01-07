#-*- coding: utf-8 -*-
""" Vimeo track source module """

import json
import sys
if sys.version_info.major == 2:
    from urllib import quote  # pylint:disable=no-name-in-module,import-error
    CHECK = unicode
elif sys.version_info.major == 3:
    from urllib.parse import quote  # pylint:disable=no-name-in-module,import-error
    CHECK = str

import vimeo
from .basesource import TrackSource

class VimeoSource(TrackSource):
    __baseurl__ = 'https://vimeo.com/'
    __priority__ = 20

    @classmethod
    def search(cls, query, max_results=25):
        """
        Run vimeo search
        """
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
