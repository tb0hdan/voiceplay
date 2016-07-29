#!/usr/bin/env python
#-*- coding: utf-8 -*-
''' VoicePlay main module '''

from __future__ import print_function
import argparse
import colorama
import json
import kaptan
import logging
import os
import platform
import pylast
import random
random.seed()
import re
import readline
import requests
import speech_recognition as sr
# Having subprocess here makes me feel sad ;-(
import signal
import subprocess
import sys
import threading
import time
import vimeo

from apiclient.discovery import build
from apiclient.errors import HttpError
from bs4 import BeautifulSoup
from dailymotion import Dailymotion
from math import trunc

if sys.version_info.major == 2:
    from Queue import Queue
    from urllib import quote
    from pipes import quote as shell_quote
    import SocketServer as socketserver
elif sys.version_info.major == 3:
    from builtins import input as raw_input
    from queue import Queue
    from urllib.parse import quote
    from shlex import quote as shell_quote
    import socketserver
else:
    raise RuntimeError('What kind of system is this?!?!')


from tempfile import mkstemp, mkdtemp
from youtube_dl import YoutubeDL


__version__ = '0.1.4'



 












