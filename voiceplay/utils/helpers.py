#-*- coding: utf-8 -*-
''' Helper functions / methods / classes '''

import hashlib
import os
from glob import glob

class Singleton(type):
    '''
    Singleton base class
    '''
    cls_instances = {}
    def __call__(cls, *args, **kwargs):
        '''
        Handle instantiation
        '''
        if cls not in cls.cls_instances:
            cls.cls_instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.cls_instances[cls]

def track_to_hash(track):
    return hashlib.sha1(track.encode('utf-8')).hexdigest()

def purge_cache():
    from voiceplay.config import Config
    from voiceplay.logger import logger
    logger.debug('Purging cache...')
    cache_dir =  Config.cfg_data().get('cache_dir', '')
    if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
        files = glob(os.path.join(cache_dir, '*'))
        for fname in files:
            try:
                os.remove(fname)
            except Exception as exc:
                logger.debug('Removal of %r failed, please check permissions')
