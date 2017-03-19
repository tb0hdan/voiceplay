#-*- coding: utf-8 -*-
""" tracksource model """

import logging
import os
import re
import sys
from youtube_dl import YoutubeDL

from voiceplay.logger import logger
from voiceplay.utils.cache import MixedCache
from voiceplay.utils.models import BaseCfgModel

class TrackSource(BaseCfgModel):
    """
    TrackSource model (parent) for actual sources
    """
    @classmethod
    def search(cls, *args, **kwargs):
        """
        Run track search
        """
        raise NotImplementedError('{0} {1}'.format(cls.__name__, 'does not provide search method'))

    @classmethod
    def download_hook(cls, response):
        """
        YDL download hook
        """
        if response['status'] == 'finished':
            logger.debug('Done downloading, now converting ...')
            cls.target_filename = response['filename']

    @classmethod
    def download(cls, trackname, url):
        """
        Run track download, use cache to store data
        """
        cache = MixedCache()
        template = os.path.join(cls.cfg_data().get('cache_dir'), cache.track_to_hash(trackname)) + '.%(ext)s'
        if isinstance(template, str) and sys.version_info.major == 2:
            template = template.decode('utf-8')
        verbose = logger.level == logging.DEBUG
        ydl_opts = {'keepvideo': False, 'verbose': verbose, 'format': 'bestaudio/best',
                    'quiet': not verbose, 'outtmpl': template,
                    'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '0',
                                        'nopostoverwrites': True, 'key': 'FFmpegExtractAudio'}],
                    'logger': logger,
                    'progress_hooks': [cls.download_hook]}

        # Try remote HTTP cache first
        result = cache.get_from_cache(os.path.join(cls.cfg_data().get('cache_dir'), cache.track_to_hash(trackname)) + '.mp3')
        if result:
            return result
        logger.debug('Using source url %s', url)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            audio_file = re.sub('\.[^\.]+$', '.mp3', cls.target_filename)
            cache.copy_to_cache(audio_file)
        return audio_file
