import hashlib
import os
from glob import glob
from .gdrive import GDrive

class MixedCache(object):

    @staticmethod
    def purge_cache():
        """
        Purge file storage cache
        """
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

    @staticmethod
    def track_to_hash(track):
        """
        Hash track name using SHA1
        """
        return hashlib.sha1(track.encode('utf-8')).hexdigest()
