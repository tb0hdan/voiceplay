#-*- coding: utf-8 -*-
""" Radionomy directory module """

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


class RadionomyResource(APIV1Resource):
    """
    Radionomy API endpoint
    """
    route_base = '/api/v1/play/radionomy/<station>'
    queue = None
    def post(self, station):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and station:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play' + ' %s ' % query + 'station from radionomy')
            result = {'status': 'ok', 'message': message}
        return result


class RadionomyClient(object):
    """
    Radionomy directory class.
    Beware of geographical restrictions
    """
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'])}

    def search(self, query):
        """
        Run radionomy directory search
        """
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
    """
    Radionomy player task
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+) station from radionomy$']
    __priority__ = 120

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message, re.I).groups()[0]
        rdc = RadionomyClient()
        url, description = rdc.search(station)[0]
        cls.say('Playing station from Radionomy' + description)
        cls.play_url(url, description)
