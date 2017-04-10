#-*- coding: utf-8 -*-
""" Crashlog module (without vendor lock-in) """

# std
import json
import os
import platform
import socket

# 3rd party
import requests

# local
from voiceplay import __version__
from voiceplay.logger import logger
from .piphelper import PIP


def exc2encode(exc_info, fname):
    """
    Exception encoder
    """
    # type, value, traceback
    result = {}
    # Probably ok
    result['name'] = exc_info[0].__name__
    result['module'] = exc_info[0].__module__
    result['lineno'] = exc_info[2].tb_lineno
    result['coname'] = exc_info[2].tb_frame.f_code.co_name
    result['hostname'] = socket.gethostname()
    result['filename'] = os.path.abspath(fname)
    result['version'] = __version__
    result['uname'] = ' '.join(platform.uname())
    result['packages'] = PIP.freeze()
    # BUGGED!
    result['value'] = repr(exc_info[1])
    result['fcode'] = repr(exc_info[2].tb_frame.f_code)
    result['lasti'] = repr(exc_info[2].tb_lasti)
    result['flocals'] = repr(exc_info[2].tb_frame.f_locals)
    result['fglobals'] = repr(exc_info[2].tb_frame.f_globals)
    #
    return json.dumps(result)


def send_traceback(exc_info, fname):
    """
    Simple bugtracker submission method
    """
    from voiceplay.config import Config
    url = Config.cfg_data().get('bugtracker_url')
    data = exc2encode(exc_info, fname)
    r = requests.post(url, data=data)
    logger.debug('Crashlog sent to %s with response code %s', url, r.status_code)
