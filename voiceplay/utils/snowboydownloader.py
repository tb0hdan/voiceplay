#-*- coding: utf-8 -*-
""" VoicePlay Snowboy downloader module """

import os
import platform
import shutil
import tarfile
import tempfile
from distutils.version import LooseVersion

import requests

from voiceplay import __issuesurl__


class SnowboyDownloader(object):
    """
    Snowboy extension downloader
    """
    def __init__(self):
        self.version = None
        self.url = None
        self.filename = tempfile.mkstemp()[1] + '.tar.bz2'
        self.tmpdir = tempfile.mkdtemp()

    def prepare_url(self):
        """
        Prepare URL based on platform information
        """
        if platform.system() == 'Darwin':
            self.version = 'osx-x86_64-1.1.0'
        else:
            # Linux distributions
            distro, version, machine = (platform.linux_distribution()[0],
                                        platform.linux_distribution()[1],
                                        platform.machine())
            if distro == 'debian' and LooseVersion(version) >= LooseVersion('8.0') and machine == 'x86_64':
                self.version = 'ubuntu1404-x86_64-1.1.0'
            elif distro == 'debian' and LooseVersion(version) < LooseVersion('7.0') and machine == 'x86_64':
                self.version = 'ubuntu1204-x86_64-1.1.0'
            elif distro == 'Ubuntu' and LooseVersion(version) >= LooseVersion('14.04') and machine == 'x86_64':
                self.version = 'ubuntu1404-x86_64-1.1.0'
            elif distro == 'Ubuntu' and LooseVersion(version) < LooseVersion('14.04') and machine == 'x86_64':
                self.version = 'ubuntu1204-x86_64-1.1.0'
            elif distro == 'CentOS Linux' and LooseVersion(version) >= LooseVersion('7.3') and machine == 'x86_64':
                self.version = 'ubuntu1404-x86_64-1.1.0'
            elif machine == 'armv7l':  # Raspberry, etc
                self.version = 'rpi-arm-raspbian-8.0-1.1.0'
            else:
                raise ValueError('Unsupported distribution, please create ticket at: {0!s}'.format(__issuesurl__))
        self.url = 'https://s3-us-west-2.amazonaws.com/snowboy/snowboy-releases/{0!s}.tar.bz2'.format(self.version)

    def download(self):
        """
        Download tarball
        """
        r = requests.get(self.url, stream=True)
        with open(self.filename, 'w') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

    def unpack(self, dest, remove=True):
        """
        Unpack tarball
        """
        archive = tarfile.open(self.filename, 'r:bz2')
        archive.extractall(path=self.tmpdir)
        try:
            os.makedirs(dest)
        except Exception as _:
            pass
        shutil.copy(os.path.join(self.tmpdir, self.version, '_snowboydetect.so'), dest)
        if remove:
            shutil.rmtree(self.tmpdir)
            os.remove(self.filename)

    def download_and_unpack(self, dest):
        """
        All-in-one wrapper
        """
        self.prepare_url()
        self.download()
        self.unpack(dest)
