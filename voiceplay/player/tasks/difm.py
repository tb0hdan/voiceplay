#-*- coding: utf-8 -*-
""" DI.FM playback task module """
""" See https://github.com/Bitcrusher/Digitally-Imported-XBMC-plugin for updates """

import json
import os
import random
random.seed()
import re
import requests

import sys
if sys.version_info.major == 2:
    from urllib import quote  # pylint:disable=no-name-in-module,import-error
elif sys.version_info.major == 3:
    from urllib.parse import quote  # pylint:disable=no-name-in-module,import-error

import tempfile
import time

from voiceplay.datasources.playlists import library_guesser
from voiceplay.logger import logger
from voiceplay.utils.requestor import WSRequestor
from .basetask import BasePlayerTask


class DIFMClient(WSRequestor):
    """
    DI.FM client
    """
    cache_file = 'difm_cache.dat'

    def get_all(self):
        response = requests.get('http://listen.di.fm/public2', headers=self.headers)
        return response.json()

    def search_and_extract(self, query):
        all_stations = self.get_check_all()
        playlist = ''
        # try full match first
        for station in all_stations:
            if query.lower() == station.get('name', '').lower():
                playlist = station.get('playlist', '')
                break
        # try word search
        if not playlist:
            word = query.split(' ')[0]
            for station in all_stations:
                if word.lower() in station.get('name', '').lower():
                    playlist = station.get('playlist', '')
                    break
        # check for pls
        if not playlist:
            return None, None
        # extract playlist items
        fname = tempfile.mkstemp()[1] + '.pls'
        with open(fname, 'w') as playlist_file:
            playlist_file.write(requests.get(playlist, headers=self.headers).text)
        playlist_url, description = library_guesser(fname, url_only=True)[0], library_guesser(fname)[0]
        os.remove(fname)
        return playlist_url, description


class DIFMTask(BasePlayerTask):
    """
    DI.FM task
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+) station from di(?:.+)?$']
    __priority__ = 180
    __actiontype__ = 'di_fm_task'

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message, re.I).groups()[0]
        difm = DIFMClient()
        url, description = difm.search_and_extract(station)
        if url:
            cls.say('Playing station from DI.FM' + description)
            cls.play_url(url, description)
        else:
            message = 'The station {0!s} could not be found'.format(station)
            cls.logger.warning(message)
            cls.say(message)