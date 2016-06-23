#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-
''' VoicePlay main module '''

__version__ = '0.0.1'

import argparse
import json
import kaptan
import logging
import os
import pylast
import random
random.seed()
import re
import speech_recognition as sr
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from youtube_dl import YoutubeDL


class MyParser(object):
    '''
    Parse text commands
    '''
    known_actions = {'play': {'^play some music by (.+)$': 'shuffle_artist',
                              '^play top tracks by (.+)$': 'top_tracks_artist',
                              '^play (.+) by (.+)$': 'single_track_artist'}}

    def __init__(self, wake_word='vicki'):
        self.wake_word = wake_word
        self.normalize_phrases = self.load_phrases(self.wake_word)

    @staticmethod
    def load_phrases(wake_word, normalize_file='normalize.json'):
        with open(normalize_file, 'rb') as normalize_fh:
            data = json.loads(normalize_fh.read())
        return data[wake_word]

    def normalize(self, sentence):
        message = sentence.lower()
        result = message
        # first pass
        for phrase in self.normalize_phrases:
            if message.startswith(phrase):
                result = re.sub(r'^%s' % phrase, self.normalize_phrases[phrase], message)
        if result != message:
            message = result
        #
        # second pass
        for phrase in self.normalize_phrases:
            if message.startswith(phrase):
                result = re.sub(r'^%s' % phrase, self.normalize_phrases[phrase], message)
        return result

    def parse(self, message):
        result = self.normalize(message)
        start = False
        action_phrase = []
        for word in result.split(' '):
            if word == self.wake_word:
                continue
            # confirm proper type
            if self.known_actions.get(word):
                start = True
            if start and word:
                action_phrase.append(word)
        action_phrase = ' '.join(action_phrase)
        return action_phrase

    def get_action_type(self, action_phrase):
        action = action_phrase.split(' ')[0]
        if self.known_actions.get(action, None) is None:
            raise ValueError('Unknown action %r in phrase %r' % (action, action_phrase))
        action_type = None
        for reg in self.known_actions.get(action):
            if re.match(reg, action_phrase) is not None:
                action_type = self.known_actions[action][reg]
                break
        if action_phrase and action_phrase.startswith('play') and not action_type:
            reg = '^play (.+)$'
            action_type = 'track_number_artist'
        return action_type, reg, action_phrase

class VoicePlayLastFm(object):
    '''
    Last.Fm API
    '''
    def __init__(self, cfg_file='config.yaml'):
        config = kaptan.Kaptan()
        config.import_config(cfg_file)
        cfg_data = config.configuration_data

        self.network = pylast.LastFMNetwork(api_key=cfg_data['lastfm']['key'],
                                            api_secret=cfg_data['lastfm']['secret'])

    def get_top_tracks(self, artist):
        '''
        Get top tracks by artist
        '''
        top_tracks = []
        aobj = pylast.Artist(artist, self.network)
        tracks = aobj.get_top_tracks()
        for track in tracks:
            top_tracks.append(track.item.artist.name + ' - ' + track.item.title)
        return top_tracks

    def get_corrected_artist(self, artist):
        '''
        Get corrected artist
        '''
        a_s = pylast.ArtistSearch(artist, self.network)
        reply = a_s.get_next_page()
        if isinstance(reply, list) and reply:
            return reply[0].name
        else:
            return ''

    def get_query_type(self, query):
        '''
        Detect whether query is just artist or artist - track
        '''
        query = query.lower()
        text = query.capitalize()
        if self.get_corrected_artist(text).lower() == text.lower():
            reply = 'artist'
        else:
            reply = 'artist_track'
        return reply

    @staticmethod
    def numerize(array):
        '''
        Name tracks
        '''
        reply = []
        for idx, element in enumerate(array):
            reply.append('%s: %s' % (idx + 1, element))
        return reply


class TextToSpeech(object):
    '''
    TODO: Add other systems
    '''
    base = 'com.apple.speech.synthesis.voice'
    def __init__(self, voice='Vicki'):
        from AppKit import NSSpeechSynthesizer
        self.voice = self.base + '.' + voice
        self.speech = NSSpeechSynthesizer.alloc().initWithVoice_(self.voice)

    def say(self, message):
        self.speech.startSpeakingString_(message)
        while self.speech.isSpeaking():
            time.sleep(0.5)


class Vicki(object):
    '''
    Vicki player class
    '''
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

    def __init__(self, cfg_file='config.yaml'):
        # logger is the earliest bird
        self.init_logger()
        #
        config = kaptan.Kaptan()
        config.import_config(cfg_file)
        self.cfg_data = config.configuration_data
        self.rec = sr.Recognizer()
        self.lfm = VoicePlayLastFm()
        self.parser = MyParser()
        self.TTS = TextToSpeech()


    def init_logger(self, name='voiceplay'):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stderr)
        self.logger.addHandler(handler)


    def run_play_cmd(self, phrase):
        '''
        Run play command
        '''
        # play number
        phrase = phrase.strip().lower()
        if not phrase:
            return
        key = str(phrase.split(' ')[0])
        arr = [v for v in self.numbers if self.numbers[v]['name'] == key or self.numbers.get(key)]
        if len(phrase.split(' ')) == 1 and arr:
            if key in self.numbers:
                key = key
            elif arr:
                key = arr[0]
            adj = self.numbers[key]['adjective']
            artist = self.get_track_by_number(key)[0]
            self.TTS.say('Playing %s track by %s' % (adj, artist))
            # play track with track number
            self.play_track_by_number(key)
        else:
            if self.lfm.get_query_type(phrase) == 'artist':
                tracks = self.lfm.get_top_tracks(self.lfm.get_corrected_artist(phrase))[:10]
                numerized = ', '.join(self.lfm.numerize(tracks))
                reply = re.sub(r'^(.+)\.\s\d\:\s', '1: ', numerized)
                self.TTS.say('Here are some top tracks by %s: %s' % (phrase,
                                                                         reply))
                # record track numbers
                self.store_tracks(tracks)
            else:
                self.play_full_track(phrase)

    def run_shuffle_artist(self, artist):
        if self.lfm.get_query_type(artist) == 'artist':
            tracks = self.lfm.get_top_tracks(self.lfm.get_corrected_artist(artist))
            random.shuffle(tracks)
            for track in tracks:
                self.play_full_track(track)

    @staticmethod
    def store_tracks(tracks):
        '''
        Store top tracks
        '''
        with open('state.txt', 'wb') as file_handle:
            for track in tracks:
                file_handle.write(track + '\n')

    def play_track_by_number(self, number):
        '''
        Play track by number
        '''
        tid = 0
        track = ''
        for idx, num in enumerate(sorted(self.numbers)):
            if num == number:
                tid = idx
                break
        self.logger.warning('Playing track: %s - %s', number, tid)
        with open('state.txt', 'rb') as file_handle:
            lines = file_handle.read()
        for idx, line in enumerate(lines.splitlines()):
            if idx == tid - 1:
                track = line
                break
        if track:
            self.play_full_track(track)

    def get_track_by_number(self, number):
        '''
        Get Artist - Track by number
        '''
        tid = 0
        track = ''
        for idx, num in enumerate(sorted(self.numbers)):
            if num == number:
                tid = idx
                break
        self.logger.warning('Getting track: %s - %s', number, tid)
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


    def youtube_search(self, query, max_results=25):
        '''
        Run youtube search
        '''
        youtube = build('youtube', 'v3', developerKey=self.cfg_data['google']['key'])
        search_response = youtube.search().list(q=query,
                                                part="id,snippet",
                                                maxResults=max_results).execute()
        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append([search_result["snippet"]["title"], search_result["id"]["videoId"]])
        return videos

    def download_hook(self, response):
        if response['status'] == 'finished':
            self.logger.warning('Done downloading, now converting ...')

    def play_full_track(self, trackname):
        '''
        Play full track
        '''
        results = self.youtube_search(trackname)
        vid = results[0][1]
        ydl_opts = {'keepvideo': False, 'verbose': False, 'format': 'bestaudio/best', 'quiet': True,
         'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '5', u'nopostoverwrites': True, u'key': u'FFmpegExtractAudio'},
                            {u'exec_cmd': u'mplayer {}; rm -f {}', u'key': u'ExecAfterDownload'}],
         'logger': self.logger,
         'progress_hooks': [self.download_hook]}

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://youtu.be/%s' % vid])


    def play_from_parser(self, message):
        parsed = self.parser.parse(message)
        action_type, reg, action_phrase = self.parser.get_action_type(parsed)
        self.logger.warning('Action type: %s' % action_type)
        if action_type == 'single_track_artist':
            track, artist = re.match(reg, action_phrase).groups()
            self.play_full_track('%s - %s' % (artist, track))
        elif action_type == 'top_tracks_artist':
            artist = re.match(reg, action_phrase).groups()[0]
            self.run_play_cmd(artist)
        elif action_type == 'shuffle_artist':
            artist = re.match(reg, action_phrase).groups()[0]
            self.TTS.say('Shuffling %s' % artist)
            self.run_shuffle_artist(artist)
        elif action_type == 'track_number_artist':
            number = re.match(reg, action_phrase).groups()[0]
            self.logger.warning(number)
            self.run_play_cmd(number)
        else:
            msg = 'Vicki thinks you said ' + message
            self.TTS.say(msg)
            self.logger.warning(msg)

    def process_request(self, request):
        try:
            self.play_from_parser(request)
        except Exception as exc:
            self.logger.error(exc)
            self.TTS.say('Vicki could not process your request')

    def run_forever(self):
        while True:
            with sr.Microphone() as source:
                msg = 'Vicki is listening'
                self.TTS.say(msg)
                self.logger.warning(msg)
                audio = self.rec.listen(source)
            try:
                result = self.rec.recognize_google(audio)
            except sr.UnknownValueError:
                msg = 'Vicki could not understand audio'
                self.TTS.say(msg)
                self.logger.warning(msg)
                result = None
            except sr.RequestError as e:
                msg = 'Recognition error'
                self.TTS.say(msg)
                self.logger.warning('{0}; {1}'.format(msg, e))
                result = None
            if result:
                self.process_request(result)
            elif result and result.lower() in ['shutdown']:
                msg = 'Vicki is shutting down, see you later'
                self.TTS.say(msg)
                self.logger.warning(msg)
                break

class MyArgumentParser(object):
    '''
    Parse command line arguments
    '''
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='VoicePlay')

    def configure(self):
        self.parser.add_argument('-c', action="store_true", default=False, dest='console',
                            help='Start console')
        self.parser.add_argument('--version', action='version', version='%(prog)s ' +  __version__)

    def parse(self, argv=None):
        argv = sys.argv if not argv else argv
        result = self.parser.parse_args(argv[1:])
        if result.console:
            from IPython import Config
            from IPython.terminal.embed import InteractiveShellEmbed
            config = Config()
            # basic configuration
            config.TerminalInteractiveShell.confirm_exit = False
            #
            embed = InteractiveShellEmbed(config=config, banner1='')
            embed.mainloop()
        else:
            vicki = Vicki()
            vicki.run_forever()

if __name__ == '__main__':
    parser = MyArgumentParser()
    parser.configure()
    parser.parse()
