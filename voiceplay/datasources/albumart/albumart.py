# -*- coding: utf-8 -*-
""" AlbumArt container """

import requests
from voiceplay.database import voiceplaydb
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.logger import logger

class AlbumArt(object):
    """
    Album art container
    """
    @staticmethod
    def set_artist_url(artist, url):
        """
        Download and save artists' album art
        """
        if not (url and url.startswith('http')):
            logger.debug('Broken url %r', url)
            return
        req = requests.get(url)
        if req.status_code == 200:
            voiceplaydb.write_artist_image(artist, req.content)

    def get(self, artist):
        """
        Get artist picture
        """
        image = None
        if not voiceplaydb.get_artist_image(artist):
            lfm = VoicePlayLastFm()
            url = lfm.get_artist_icon(artist)
            self.set_artist_url(artist, url)
        image = voiceplaydb.get_artist_image(artist)
        return image
