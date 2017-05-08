#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import platform
import re
import sys
import subprocess
from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages
from voiceplay import (__title__,
                       __version__,
                       __description__,
                       __author__,
                       __author_email__,
                       __copyright__,
                       __file__ as vpfile)

if os.path.exists('README.rst'):
    readme = io.open('README.rst', mode='r', encoding='utf8').read()
else:
    readme = ''

system_specific_packages = ['pyobjc'] if platform.system() == 'Darwin' else ['pyfestival', 'Skype4Py']

# hook to pip install for package sideloading
# broken pyaudio package
# snowboy extension
if sys.argv[1] in ['bdist_wheel', 'install']:
    # pyaudio
    if platform.system() == 'Darwin':
        subprocess.call(['pip', 'install', '--global-option=build_ext',
                                           '--global-option=-I/usr/local/include',
                                           '--global-option=-L/usr/local/lib', 'pyaudio'])
    else:
        subprocess.call(['pip', 'install', 'pyaudio'])
    # snowboy
    from voiceplay.utils.snowboydownloader import SnowboyDownloader
    sd = SnowboyDownloader()
    # get_python_lib returns different directory when installing packages system-wide
    # TODO: FIX THIS!
    sd.download_and_unpack(os.path.join(get_python_lib(), 'voiceplay', 'extlib', 'snowboydetect'))
    sd.download_and_unpack(os.path.join(get_python_lib().replace('/usr/lib', '/usr/local/lib'), 'voiceplay', 'extlib', 'snowboydetect'))


setup(name='voiceplay',
      version=__version__,
      description=__description__,
      author=__author__,
      author_email=__author_email__,
      url='https://github.com/tb0hdan/voiceplay',
      packages=find_packages(exclude=['snowboy', 'vlcpython', 'docs', 'tests*']),
      package_data={'': ['snowboydetect/resources/*.pmdl', 'snowboydetect/resources/*.res', 
                         'snowboydetect/*.py', 'config/*.sample']},
      zip_safe=False,
      license=__copyright__,
      keywords='voiceplay music playlists vlc player',
      long_description=readme,
      dependency_links=['https://github.com/tb0hdan/mplayer.py/tarball/master#egg=mplayer.py-0.7.0beta'],
      install_requires=['Babel', 'beautifulsoup4', 'colorama', 'dailymotion', 'filemagic', 'flake8',
                        'oauth2client>=1.5.2,<4.0.0', 'requests', 'lxml', 'flask-classy', 'flask-restful',
                        'future', 'gntp', 'dropbox',
                        'google-api-python-client', 'ipython>=5.0.0,<6.0.0', 'kaptan', 'monotonic', 'gunicorn',
                        'musicbrainzngs', 'mutagen', 'mplayer.py>=0.7.0beta',
                        'piprot', 'pocketsphinx', 'pony',
                        'pylast', 'pylint', 'pytest', 'pytest-coverage', 'PyVimeo', 'rl',
                        'SpeechRecognition', 'tqdm', 'youtube-dl', 'zeroconf'] + system_specific_packages,
      entry_points={'console_scripts': [
                        'voiceplay=voiceplay.cli:main']},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: Public Domain',
          'Natural Language :: English',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet',
          'Topic :: Multimedia :: Sound/Audio :: Players',
          'Topic :: Terminals',
      ],
)
