#-*- coding: utf-8 -*-
""" VoicePlay PIP wrapper, for updates etc. """

import codecs
import contextlib
import sys
from io import BytesIO

from pip.commands.freeze import FreezeCommand
from pip.commands.search import SearchCommand, transform_hits


@contextlib.contextmanager
def capture_std():
    """
    STDOUT capture
    """
    std_out, std_err = sys.stdout, sys.stderr
    try:
        if sys.version_info.major == 3:
            out = [codecs.getwriter("utf8")(BytesIO()), codecs.getwriter("utf8")(BytesIO())]
        else:
            out = [BytesIO(), BytesIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = std_out, std_err
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


class PIP(object):
    """
    pip wrapper
    """
    @staticmethod
    def search_packages(package_name):
        """
        query pip package repository
        """
        versions = []
        search = SearchCommand()
        pypi = search.search(package_name,
                             search.parse_args([package_name])[0])
        for hit in transform_hits(pypi):
            if hit['name'] == package_name:
                versions = hit['versions']
                break
        return versions

    @staticmethod
    def freeze():
        """
        pip freeze equivalent
        """
        freeze = FreezeCommand()
        with capture_std() as std:
            freeze.run(freeze.parse_args([])[0], '')
        packages = []
        for line in std[0].splitlines():
            if sys.version_info.major == 3:
                line = line.decode()
            packages.append(line)
        return packages
