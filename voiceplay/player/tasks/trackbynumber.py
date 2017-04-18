#-*- coding: utf-8 -*-
""" Track by number task module """


import re
from voiceplay.logger import logger
#from voiceplay.webapp.baseresource import APIV1Resource
from .basetask import BasePlayerTask


class TrackByNumberTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = ['^play top (?:songs|tracks) by (.+)$']
    __priority__ = 30

    numbers = {'1': {'name': 'one', 'adjective': 'first'},
               '2': {'name': 'two', 'adjective': 'second'},
               '3': {'name': 'three', 'adjective': 'third'},
               '4': {'name': 'four', 'adjective': 'fourth'},
               '5': {'name': 'five', 'adjective': 'fifth'},
               '6': {'name': 'six', 'adjective': 'sixth'},
               '7': {'name': 'seven', 'adjective': 'seventh'},
               '8': {'name': 'eight', 'adjective': 'eighth'},
               '9': {'name': 'nine', 'adjective': 'ninth'},
               '10': {'name': 'ten', 'adjective': 'tenth'}}

    @classmethod
    def run_play_cmd(cls, phrase):
        """
        Run play command
        """
        # play number
        phrase = phrase.strip().lower()
        if not phrase:
            return
        key = str(phrase.split(' ')[0])
        arr = [v for v in cls.numbers if cls.numbers[v]['name'] == key or cls.numbers.get(key)]
        if len(phrase.split(' ')) == 1 and arr:
            if key in cls.numbers:
                key = key
            elif arr:
                key = arr[0]
            adj = cls.numbers[key]['adjective']
            artist = cls.get_track_by_number(key)[0]
            cls.say('Playing %s track by %s' % (adj, artist))
            # play track with track number
            cls.play_track_by_number(key)
        else:
            if cls.lfm().get_query_type(phrase) == 'artist':
                tracks = cls.lfm().get_top_tracks(cls.lfm().get_corrected_artist(phrase))[:10]
                numerized = ', '.join(cls.lfm().numerize(tracks))
                reply = re.sub(r'^(.+)\.\s\d\:\s', '1: ', numerized)
                cls.say('Here are some top tracks by %s: %s' % (phrase,
                                                                reply))
                # record track numbers
                cls.store_tracks(tracks)
            else:
                cls.play_full_track(phrase)

    @staticmethod
    def store_tracks(tracks):
        """
        Store top tracks
        TODO: Use DB instead
        """
        with open('state.txt', 'wb') as file_handle:
            for track in tracks:
                file_handle.write(track + '\n')

    @classmethod
    def play_track_by_number(cls, number):
        """
        Play track by number
        """
        tid = 0
        track = ''
        for idx, num in enumerate(sorted(cls.numbers)):
            if num == number:
                tid = idx if idx > 1 else idx + 1
                break
        logger.warning('Playing track: %s - %s', number, tid)
        with open('state.txt', 'rb') as file_handle:
            lines = file_handle.read()
        for idx, line in enumerate(lines.splitlines()):
            if idx == tid - 1:
                track = line
                break
        if track:
            cls.play_full_track(track)

    @classmethod
    def get_track_by_number(cls, number):
        """
        Get Artist - Track by number
        """
        tid = 0
        track = ''
        for idx, num in enumerate(sorted(cls.numbers)):
            if num == number:
                tid = idx if idx > 1 else idx + 1
                break
        logger.warning('Getting track: %s - %s', number, tid)
        with open('state.txt', 'rb') as file_handle:
            lines = file_handle.read()
        full_track = ''
        for idx, line in enumerate(lines.splitlines()):
            if idx == tid - 1:
                full_track = line
                break
        if full_track:
            artist = full_track.split(' - ')[0]
            track = full_track.split(' - ')[1]
        else:
            artist = 'unknown'
            track = 'unknown'
        return artist, track

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        artist = re.match(regexp, message, re.I).groups()[0]
        artist = cls.lfm().get_corrected_artist(artist)
        cls.run_play_cmd(artist)
