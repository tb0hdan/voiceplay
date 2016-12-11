#-*- coding: utf-8 -*-

import logging
import os
import re

from youtube_dl import YoutubeDL

from voiceplay.config import Config
from voiceplay.logger import logger
from voiceplay.utils.helpers import track_to_hash

class TrackSource(object):
    '''
    '''
    cfg_data = Config.cfg_data()

    @classmethod
    def search(cls, *args, **kwargs):
        raise NotImplementedError('{0} {1}'.format(cls.__name__, 'does not provide search method'))

    @classmethod
    def download_hook(cls, response):
        '''
        YDL download hook
        '''
        if response['status'] == 'finished':
            logger.debug('Done downloading, now converting ...')
            cls.target_filename = response['filename']

    @classmethod
    def download(cls, trackname, url):
        template = os.path.join(cls.cfg_data.get('cache_dir'), track_to_hash(trackname)) + '.%(ext)s'
        if isinstance(template, str):
            template = template.decode('utf-8')
        verbose = logger.level == logging.DEBUG
        ydl_opts = {'keepvideo': False, 'verbose': verbose, 'format': 'bestaudio/best',
                    'quiet': not verbose, 'outtmpl': template,
                    'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '0',
                                        'nopostoverwrites': True, 'key': 'FFmpegExtractAudio'}],
                    'logger': logger,
                    'progress_hooks': [cls.download_hook]}

        logger.debug('Using source url %s', url)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            audio_file = re.sub('\.[^\.]+$', '.mp3', cls.target_filename)
        return audio_file
