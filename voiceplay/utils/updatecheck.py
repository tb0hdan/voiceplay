#-*- coding: utf-8 -*-
""" Primitive update checker """

import json
from distutils.version import LooseVersion

from voiceplay import __version__, __title__
from voiceplay.database import voiceplaydb
from .piphelper import PIP


def check_update(my_version=__version__, suppress_uptodate=False):
    """
    Check for application update and notify user
    """
    result = ''
    low_title = __title__.lower()
    packages = voiceplaydb.get_cached_service('check_update')
    if not packages:
        packages = PIP.search_packages(low_title)
        if packages:
            voiceplaydb.set_cached_service('check_update', json.dumps(packages))
    else:
        packages = json.loads(packages)
    for version in packages:
        if LooseVersion(version) == LooseVersion(my_version) and not suppress_uptodate:
            result = "You're running {0!s} which is latest version.".format(my_version)
            break
        elif LooseVersion(version) > LooseVersion(my_version):
            result = "You are using {0!s} version {1!s}, however version {2!s} is available.\n".format(low_title, my_version, version)
            result += "You should consider upgrading via the 'pip install --upgrade {0!s}' command.".format(low_title)
    return result
