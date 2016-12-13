#-*- coding: utf-8 -*-
''' Helper functions / methods / classes '''

import hashlib
import os
import sys
import threading
import time
import traceback
from glob import glob

from voiceplay.logger import logger

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

def restart_on_crash(method, *args, **kwargs):
    while True:
        result = None
        try:
            result = method(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as exc:
            exc_type, exc_value, exc_trace = sys.exc_info()
            trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_trace))
            logger.debug('Method %r crashed with %r:%s, restarting...', method, exc.message, trace)
            # allow interrupt
            time.sleep(1)
        else:
            break
    logger.debug('Method %r completed without exception', method)
    return result

class ThreadGroup(object):
    """
    """
    def __init__(self, daemon=True, timeout=1.0, restart=True):
        self.daemon = daemon
        self.restart = restart
        self.threads = []
        self._targets = []
        self.timeout = timeout

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, th):
        self._targets = th

    def start_all(self):
        for target in self._targets:
            args = ()
            name = repr(target)
            if self.restart:
                args = (target,)
                target = restart_on_crash
            thread = threading.Thread(name=name, target=target, args=args)
            thread.daemon = self.daemon
            thread.start()
            self.threads.append(thread)

    def stop_all(self):
        for thread in self.threads:
            thread.join(timeout=self.timeout)
