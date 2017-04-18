#-*- coding: utf-8 -*-
""" TuneIn playback task module """


import json
import random
random.seed()
import re

from future.standard_library import install_aliases
install_aliases()

from urllib.parse import quote  # pylint:disable=no-name-in-module,import-error

import requests

from bs4 import BeautifulSoup

from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class TuneInResource(APIV1Resource):
    """
    TuneIn API endpoint
    """
    route_base = '/api/v1/play/tunein/<station>'
    queue = None
    def post(self, station):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and station:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play' + ' %s ' % station + 'from tunein')
            result = {'status': 'ok', 'message': message}
        return result


class TuneInClient(object):
    """
    TuneIn client
    TODO: Move out requestor to voiceplay.utils
    """
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'])}

    def search(self, query):
        """
        Run TuneIn search
        """
        stations = []
        data = requests.get('http://tunein.com/search/?query={0!s}'.format(quote(query)), headers=self.headers)
        soup = BeautifulSoup(''.join(data.text), 'html.parser')
        for element in soup.find_all(lambda tag: tag.name == 'a' and 'profile-link' in tag.get('class', []) and '/radio/' in tag.get('href', '')):
            stream_info_url = ''
            stream_info_title = ''
            if element.name == 'a':
                stream_info_url = element.get('href')
                for x in element.find_all():
                    if x.name == 'h3' and 'title' in x.get('class', []):
                        stream_info_title = x.text
                        break
                if stream_info_url and stream_info_title:
                    stations.append(['http://tunein.com' + stream_info_url, stream_info_title])
        return stations

    def get_station_info(self, station_url):
        """
        Get station info (i.e. extract JS from HTML)
        """
        data = requests.get(station_url, headers=self.headers)
        soup = BeautifulSoup(''.join(data.text), 'html.parser')
        for element in soup.find_all(lambda tag: tag.name == 'script'):
            if not 'TuneIn.payload' in element.text:
                continue
            for line in element.text.splitlines():
                if not 'TuneIn.payload' in line:
                    continue
                data = json.loads(re.sub('TuneIn.payload =', '', line.strip()))
        return data

    @staticmethod
    def extract_streamurl(station_data):
        """
        Extract stream url from station info
        """
        for kw in ['Station', 'Program']:
            station_url = station_data.get(kw, {}).get('broadcast', {}).get('StreamUrl', '')
            if station_url and not station_url.startswith('http://') and station_url.startswith('//'):
                station_url = 'http:' + station_url
            if station_url:
                break
        return station_url

    def extract_stream(self, stream_url):
        """
        Extract stream from stream URL
        """
        data = requests.get(stream_url, headers=self.headers)
        streams = data.json().get('Streams')
        streams = [param for param in streams if param.get('HasPlaylist', False) is False]
        streams = sorted(streams, key=lambda param: param.get('Bandwidth'), reverse=True)
        url = []
        if streams:
            url = streams[0].get('Url', '')
        return url

    def search_and_extract(self, query):
        """
        All-in-one method, returns playable stream url
        """
        stations = self.search(query)
        # do match here?
        station_url = stations[0][0]
        station_description = stations[0][1]
        info_url = self.get_station_info(station_url)
        stream_url = self.extract_streamurl(info_url)
        real_stream = self.extract_stream(stream_url)
        # [] -> None
        if not real_stream:
            real_stream = None
        return real_stream, station_description


class TuneInTask(BasePlayerTask):
    """
    TuneIn task
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+) station from tunein$']
    __priority__ = 110

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message, re.I).groups()[0]
        tic = TuneInClient()
        url, description = tic.search_and_extract(station)
        if url:
            cls.say('Playing station from TuneIn' + description)
            cls.play_url(url, description)
        else:
            message = 'The station {0!s} could not be found'.format(station)
            cls.logger.warning(message)
            cls.say(message)
