#-*- coding: utf-8 -*-
""" IceCast directory search """

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


class IceCastResource(APIV1Resource):
    """
    IceCast API endpoint
    """
    route_base = '/api/v1/play/icecast/<station>'
    queue = None
    def post(self, station):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and station:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play' + ' %s ' % query + 'station from icecast')
            result = {'status': 'ok', 'message': message}
        return result


class IcecastClient(object):
    """
    IceCast directory client
    """
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'])}

    def search(self, query):
        """
        Run directory search
        """
        stations = []
        data = requests.get('http://dir.xiph.org/search?search={0!s}'.format(quote(query)), headers=self.headers)
        soup = BeautifulSoup(''.join(data.text), 'html.parser')
        for element in soup.find_all(lambda tag: tag.name == 'td' and 'tune-in' in tag.get('class', [])):
            for x in element.find_all(lambda tag: tag.name == 'a' and 'm3u' in tag.get('href')):
                url = x.get('href', '')
                title = x.get('title', '')
                if url and title:
                    # title len if limited
                    # TODO: fix this later :)
                    m3u_url = 'http://dir.xiph.org' + url
                    stations.append([m3u_url, re.sub('(^Listen to \'|\'$)', '', title)])
        return stations

    def extract_streams(self, m3u_url):
        """
        Extract stream urls from playlist
        """
        streams = []
        data = requests.get(m3u_url, headers=self.headers)
        for stream in data.text.splitlines():
            streams.append(stream)
        return streams


class IcecastTask(BasePlayerTask):
    """
    IceCast directory task
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+) station from icecast$']
    __priority__ = 130

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message, re.I).groups()[0]
        icc = IcecastClient()
        m3u_url, description = icc.search(station)[0]
        url = icc.extract_streams(m3u_url)[0]
        cls.say('Playing station from Icecast' + description)
        cls.play_url(url, description)
