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


class RadionomyClient(object):
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'
                                            ])}

    def search(self, query):
        stations = []
        data = requests.get('http://www.radionomy.com/en/search/index?query={0!s}'.format(quote(query)), headers=self.headers)
        soup = BeautifulSoup(''.join(data.text), 'html.parser')
        for element in soup.find_all(lambda tag: tag.name == 'div' and 'radioPlayBtn' in tag.get('class', [])):
            info = element.get('data-play-stream')
            station_info = json.loads(info)
            title = station_info.get('title', '')
            url = station_info.get('mp3', '')
            if title and url:
                stations.append([url, title])
        return stations


class RadionomyTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = ['^play (.+) station from radionomy$']
    __priority__ = 120
    __actiontype__ = 'radionomy_task'

    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message).groups()[0]
        rdc = RadionomyClient()
        url, description = rdc.search(station)[0]
        cls.say('Playing station from Radionomy' + description)
        cls.play_url(url, description)