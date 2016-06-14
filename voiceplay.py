#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-
''' VoicePlay main module '''

import kaptan
import pylast
import re
import speech_recognition as sr
import subprocess

from apiclient.discovery import build
from apiclient.errors import HttpError


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
    @classmethod
    def say(cls, message):
        subprocess.call(['say', '-v', 'Vicki', message], shell=False)


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
        config = kaptan.Kaptan()
        config.import_config(cfg_file)
        self.cfg_data = config.configuration_data
        self.rec = sr.Recognizer()
        self.lfm = VoicePlayLastFm()

    def run_play_cmd(self, phrase):
        '''
        Run play command
        '''
        # play number
        phrase = phrase.strip().lower()
        if not phrase:
            return
        key = str(phrase.split(' ')[0])
        if len(phrase.split(' ')) == 1 and key in self.numbers:
            adj = self.numbers[key]['adjective']
            artist = self.get_track_by_number(key)[0]
            TextToSpeech.say('Playing %s track by %s' % (adj, artist))
            # play track with track number
            self.play_track_by_number(key)
        else:
            if self.lfm.get_query_type(phrase) == 'artist':
                tracks = self.lfm.get_top_tracks(self.lfm.get_corrected_artist(phrase))[:10]
                numerized = ', '.join(self.lfm.numerize(tracks))
                reply = re.sub(r'^(.+)\.\s\d\:\s', '1: ', numerized)
                TextToSpeech.say('Here are some top tracks by %s: %s' % (phrase,
                                                                         reply))
                # record track numbers
                self.store_tracks(tracks)
            else:
                self.play_full_track(phrase)

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
        print 'Playing track: %s - %s' % (number, tid)
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
        print 'Getting track: %s - %s' % (number, tid)
        with open('state.txt', 'rb') as file_handle:
            lines = file_handle.read()
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

    def play_full_track(self, trackname):
        '''
        Play full track
        '''
        results = self.youtube_search(trackname)
        vid = results[0][1]
        subprocess.call(['youtube-dl', '-q', '-x', '--no-post-overwrites', '--audio-format',
                         'mp3', '--exec', 'mplayer {}; rm -f {}', 'https://youtu.be/%s' % vid])

    def play_from_message(self, message):
        '''
        Parse and play track from message
        '''
        track = re.sub(r'^[W|w|V|v]ic?k(i|ed)?\s(p?[L|l]?ate|[P|p]?lay|[B|b]?lade)\s+', '', message)
        print ('Track: %s' % track)
        self.run_play_cmd(track)


if __name__ == '__main__':
    keywords = ['vicki', 'wiki', 'wicked', 'vk', 'we can', 'wickedly']
    vicki = Vicki()
    while True:
        with sr.Microphone() as source:
            msg = 'Vicki is listening'
            TextToSpeech.say(msg)
            print(msg)
            audio = vicki.rec.listen(source)
        try:
            result = vicki.rec.recognize_google(audio)
        except sr.UnknownValueError:
            msg = 'Vicki could not understand audio'
            TextToSpeech.say(msg)
            print(msg)
            result = None
        except sr.RequestError as e:
            msg = 'Recognition error'
            TextToSpeech.say(msg)
            print('{0}; {1}'.format(msg, e))
            result = None
        if result and [res for res in keywords if result.lower().startswith(res)]:
            vicki.play_from_message(result)
        elif result and result.lower() in ['shutdown']:
            msg = 'Vicki is shutting down, see you later'
            TextToSpeech.say(msg)
            print(msg)
            break
        elif result:
            msg = 'Vicki thinks you said ' + result
            TextToSpeech.say(msg)
            print(msg)
