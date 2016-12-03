import os
import random
random.seed()
import re
from voiceplay.logger import logger
from .basetask import BasePlayerTask


class LocalLibraryTask(BasePlayerTask):

    __group__ = ['play', 'shuffle']
    __regexp__ = ['^play (.+)?my library$', '^shuffle (.+)?my library$']
    __priority__ = 50
    __actiontype__ = 'shuffle_local_library'

    @classmethod
    def play_local_library(cls, message):
        fnames = []
        library = os.path.expanduser('~/Music')
        for root, _, files in os.walk(library, topdown=False):
            for name in files:
                if name.lower().endswith('.mp3'):
                    fnames.append(os.path.join(root, name))
        random.shuffle(fnames)
        for fname in fnames:
            if cls.get_exit():
                break
            cls.player.play(fname, fname.rstrip('.mp3'))

    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Running task: %s with %r -> %r', 'LocalLibraryTask', regexp, message)
        msg = re.match(regexp, message).groups()[0]
        logger.warning(msg)
        cls.tts.say_put('Shuffling songs in local library')
        cls.play_local_library(msg)
