#-*- coding: utf-8 -*-
""" Pleer.net track source module """

import json
import os
import sys


import requests

from future.standard_library import install_aliases
install_aliases()

from urllib.parse import quote

from bs4 import BeautifulSoup
from magic import Magic

from voiceplay.utils.cache import MixedCache

from .basesource import TrackSource


class PleerSource(TrackSource):
    """
    Pleer.net track source
    """
    __baseurl__ = 'http://pleer.net/en/download/page/'
    __priority__ = 10
    chunk_size = 8196

    @classmethod
    def search(cls, query, max_results=25):
        """
        Run track source
        """
        if sys.version_info.major == 2:
            CHECK = unicode
        elif sys.version_info.major == 3:
            CHECK = str
        if isinstance(query, CHECK):
            query = query.encode('utf-8')
        term = quote(query)
        url = 'http://pleer.net/search?page=1&q=%s&sort_mode=0&sort_by=0&quality=all&onlydata=true' % quote(query)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.net/search?q=%s' % term}
        r = requests.get(url, headers=headers, timeout=10)
        result = json.loads(r.text).get('html', '')
        soup = BeautifulSoup(''.join(result), 'html.parser')
        tracks = []
        for el in soup.findAll(lambda tag: tag.name == 'div' and tag.a and tag.a['href'] == '#'):
            tg = el.findParent()
            if not tg.name == 'li':
                continue
            title = '%s - %s' % (tg.get('singer'), tg.get('song'))
            aid = tg.get('link')
            tracks.append([title, aid])
        return tracks

    @classmethod
    def download(cls, track_name, track_url):
        """
        Download track
        """
        cache = MixedCache()
        filename = os.path.join(cls.cfg_data().get('cache_dir'), cache.track_to_hash(track_name)) + '.mp3'
        # Try remote HTTP cache first
        result = cache.get_from_cache(filename)
        if result:
            return result
        track_id = track_url.replace('http://pleer.net/en/download/page/', '')
        url = 'http://pleer.net/site_api/files/get_url'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.net/en/download/page/%s' % track_id}
        reply = requests.post(url, data={'action': 'download', 'id': track_id}, timeout=10)
        result = json.loads(reply.text).get('track_link')
        r = requests.get(result, headers=headers, stream=True, timeout=10)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(cls.chunk_size):
                fd.write(chunk)
        with Magic() as magic:
            ftype = magic.id_filename(filename)
            if ftype.startswith('HTML'):
                filename = None
        if filename:
            cache.copy_to_cache(filename)
        return filename
