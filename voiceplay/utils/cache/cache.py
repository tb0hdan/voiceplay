#-*- coding: utf-8 -*-
""" Cache module """

import hashlib
import os
import random
random.seed()

from glob import glob

from voiceplay.logger import logger

from .gdrive import GDrive
from .dbox import DBox


class BaseCache(object):
    """
    Parent cache class with common methods
    """
    @classmethod
    def is_remote_cached(cls, target_filename):
        """
        Return remote file ID if it is cached
        """
        is_cached = None
        cache = cls.CACHE_BACKEND()
        for file_name, file_id in cache.search():
            if file_name == os.path.basename(target_filename):
                is_cached = file_id
                logger.debug('File %r already cached at %r', target_filename, cls.CACHE_BACKEND)
                break
        return is_cached

    @classmethod
    def copy_to_cache(cls, target_filename):
        """
        Transfer file to cache (if it is not cached, of course)"
        """
        is_cached = cls.is_remote_cached(target_filename)
        if not is_cached:
            cache = cls.CACHE_BACKEND()
            cache.upload(target_filename)
            logger.debug('File %r was uploaded to %r', target_filename, cls.CACHE_BACKEND)

    @classmethod
    def get_from_cache(cls, target_filename):
        """
        Get file from cache
        """
        is_cached = cls.is_remote_cached(target_filename)
        if is_cached:
            cache = cls.CACHE_BACKEND()
            cache.download(is_cached, target_filename)
            logger.debug('File %r was downloaded from %r', target_filename, cls.CACHE_BACKEND)
        else:
            target_filename = None
        return target_filename

    @classmethod
    def health_check(cls):
        """
        Cache health check (space availability)
        """
        cb = cls.CACHE_BACKEND()
        return cb.health_check()


class DBoxCache(BaseCache):
    """
    Cache using Dropbox
    """
    CACHE_BACKEND = DBox


class GDriveCache(BaseCache):
    """
    Cache using Google Drive
    """
    CACHE_BACKEND = GDrive


class MixedCache(object):
    """
    Multi-backend cache
    """
    CACHE_BACKENDS = [DBoxCache, GDriveCache]

    @staticmethod
    def purge_cache():
        """
        Purge file storage cache
        """
        from voiceplay.config import Config
        logger.debug('Purging cache...')
        cache_dir = Config.cfg_data().get('cache_dir', '')
        if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
            files = glob(os.path.join(cache_dir, '*'))
            for fname in files:
                try:
                    os.remove(fname)
                except Exception as exc:
                    logger.debug('Removal of %r failed, please check permissions', exc)

    @staticmethod
    def track_to_hash(track):
        """
        Hash track name using SHA1
        """
        return hashlib.sha1(track.encode('utf-8')).hexdigest()

    @classmethod
    def get_from_cache(cls, file_name):
        """
        Iterate over available cache backends, search for file, return first matching copy
        """
        random.shuffle(cls.CACHE_BACKENDS)
        fname = None
        for cb in cls.CACHE_BACKENDS:
            if not cb.health_check():
                continue
            fname = cb.get_from_cache(file_name)
            if fname:
                break
        return fname

    @classmethod
    def copy_to_cache(cls, file_name):
        """
        Iterate over available cache backends, upload to first one. Primitive load balancing
        is implemented by randomizing backend list.
        """
        random.shuffle(cls.CACHE_BACKENDS)
        for cb in cls.CACHE_BACKENDS:
            if not cb.health_check():
                continue
            # attempt upload
            cb.copy_to_cache(file_name)
            # confirm presence
            if cls.get_from_cache(file_name):
                break
