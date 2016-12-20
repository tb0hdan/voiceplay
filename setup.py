#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re
import platform
from setuptools import setup, find_packages
from voiceplay import __title__, __version__, __description__, __author__, __author_email__, __copyright__

if os.path.exists('README.md'):
    readme = io.open('README.md', mode='r', encoding='utf8').read()
else:
    readme = ''

system_specific_packages = ['gntp', 'pyobjc'] if platform.system() == 'Darwin' else ['pyfestival']
setup(name='voiceplay',
      version=__version__,
      description=__description__,
      author=__author__,
      author_email=__author_email__,
      url='https://github.com/tb0hdan/voiceplay',
      packages=find_packages(exclude=['snowboy', 'vlcpython', 'docs', 'tests*']),
      package_data={'': ['resources/*.pmdl', 'resources/*.res']},
      zip_safe=False,
      license=__copyright__,
      keywords='voiceplay music playlists vlc player',
      long_description=readme,
      install_requires=['Babel', 'beautifulsoup4', 'colorama', 'dailymotion', 'filemagic', 'flake8',
                        'google-api-python-client', 'ipython', 'kaptan', 'monotonic',
                        'musicbrainzngs', 'mutagen', 'piprot', 'pocketsphinx', 'pony', 'PyAudio',
                        'pylast', 'pylint', 'pytest', 'pytest-coverage', 'PyVimeo', 'rl', 'Skype4Py',
                        'SpeechRecognition', 'youtube-dl'] + system_specific_packages,
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
          'Topic :: Internet',
          'Topic :: Multimedia :: Sound/Audio :: Players',
          'Topic :: Terminals',
      ],
)
