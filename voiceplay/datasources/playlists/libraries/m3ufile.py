#-*- coding: utf-8 -*-
""" M3U playlist module """


import re

class M3UFileLibrary(object):
    """
    Very basic and silly extended M3U parser
    """
    @staticmethod
    def m3u_parser(data):
        """
        .m3u file parser
        """
        tracks = []
        for line in data.splitlines():
            track = line.strip()
            if not track.lower().startswith('#extinf:'):
                continue
            track = re.sub(r'#extinf:\d+,', '', track, flags=re.IGNORECASE)
            if track:
                tracks.append(track)
        return tracks

    def parse(self, library_file):
        """
        Process M3U playlist, return items
        """
        tracks = []
        with open(library_file, 'rb') as m3u_file:
            data = m3u_file.read()
            data = data.decode()
            tracks = self.m3u_parser(data)
        return tracks
