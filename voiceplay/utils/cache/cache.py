
import hashlib
import os
from glob import glob

from voiceplay.logger import logger

from .gdrive import GDrive

class MixedCache(object):
    CACHE_BACKEND = GDrive

    @staticmethod
    def purge_cache():
        """
        Purge file storage cache
        """
        from voiceplay.config import Config
        logger.debug('Purging cache...')
        cache_dir =  Config.cfg_data().get('cache_dir', '')
        if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
            files = glob(os.path.join(cache_dir, '*'))
            for fname in files:
                try:
                    os.remove(fname)
                except Exception as exc:
                    logger.debug('Removal of %r failed, please check permissions')

    @staticmethod
    def track_to_hash(track):
        """
        Hash track name using SHA1
        """
        return hashlib.sha1(track.encode('utf-8')).hexdigest()

    @classmethod
    def is_remote_cached(cls, target_filename):
        """
        Return remote file ID if it is cached
        """
        is_cached = None
        cache = cls.CACHE_BACKEND()
        for file_id, file_name in cache.search():
            if file_name == os.path.basename(target_filename):
                is_cached = file_id
                logger.debug('File %r already cached at %r', target_filename, cls.CACHE_BACKEND)
                break
        return is_cached

    @classmethod
    def copy_to_cache(cls, target_filename):
        is_cached = cls.is_remote_cached(target_filename)
        if not is_cached:
            cache = cls.CACHE_BACKEND()
            cache.upload(target_filename)
            logger.debug('File %r was uploaded to %r', target_filename, cls.CACHE_BACKEND)

    @classmethod
    def get_from_cache(cls, target_filename):
        is_cached = cls.is_remote_cached(target_filename)
        if is_cached:
            cache = cls.CACHE_BACKEND()
            cache.download(is_cached, target_filename)
            logger.debug('File %r was downloaded from %r', target_filename, cls.CACHE_BACKEND)
        return is_cached
