#-*- coding: utf-8 -*-

import json
import random
random.seed()
import re
import requests
import time

from bs4 import BeautifulSoup
from urllib import quote

from voiceplay.logger import logger
from .basetask import BasePlayerTask


class TuneInClient(object):
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'
                                            ])}

    def search(self, query):
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
        station_url = station_data.get('Station', {}).get('broadcast', {}).get('StreamUrl', '')
        if not station_url.startswith('http://') and station_url.startswith('//'):
            station_url = 'http:' + station_url
        return station_url

    def extract_stream(self, stream_url):
        data = requests.get(stream_url, headers=self.headers)
        streams = data.json().get('Streams')
        streams = filter(lambda param: param.get('HasPlaylist', False) is False, streams)
        streams = sorted(streams, key=lambda param: param.get('Bandwidth'), reverse=True)
        url = []
        if streams:
            url = streams[0].get('Url', '')
        return url

    def search_and_extract(self, query):
        stations = self.search(query)
        # do match here?
        station_url = stations[0][0]
        station_description = stations[0][1]
        info_url = self.get_station_info(station_url)
        stream_url = self.extract_streamurl(info_url)
        real_stream = self.extract_stream(stream_url)
        return real_stream, station_description


class TuneInTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = ['^play (.+) station from tunein$']
    __priority__ = 110
    __actiontype__ = 'tune_in_task'

    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message).groups()[0]
        tic = TuneInClient()
        url, description = tic.search_and_extract(station)
        cls.say('Playing station from TuneIn' + description)
        cls.play_url(url, description)