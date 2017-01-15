#-*- coding: utf-8 -*-

import re

class PLSFileLibrary(object):
    '''
    Very basic and silly PLS parser
    '''
    def __init__(self):
        pass

    def pls_parser(self, data, url_only=False):
        tracks = []
        for line in data.splitlines():
            track = line.strip()
            if not url_only:
                if not track.lower().startswith('title'):
                    continue
                track = re.sub(r'title\d+?\=', '', track, flags=re.IGNORECASE)
            else:
                if not track.lower().startswith('file'):
                    continue
                track = re.sub(r'file\d+?\=', '', track, flags=re.IGNORECASE)
            if track:
                tracks.append(track)
        return tracks

    def parse(self, library_file, url_only=False):
        tracks = []
        with open(library_file, 'rb') as pls_file:
            data = pls_file.read()
            data = data.decode()
            tracks = self.pls_parser(data, url_only=url_only)
        return tracks
