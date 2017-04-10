#-*- coding: utf-8 -*-
''' Shazam module for 'Download History' '''


from bs4 import BeautifulSoup

class ShazamDownloadLibrary(object):
    """
    Shazam 'Download History' Library
    """
    @staticmethod
    def html_parser(data):
        """
        Shazam (HTML) parser using BeautifulSoup
        """
        soup = BeautifulSoup(''.join(data), 'lxml')
        tracks = []
        for entry in soup.findAll(lambda tag: tag.name == 'td' and tag.get('class') == None):
            prev = entry.find_previous()
            if prev.a and 'shz.am' in prev.a['href']:
                track = entry.a.text
                for e in prev.findAll(lambda tag: tag.name == 'td' and tag.get('class') == None and not tag.a):
                    artist = e.text
                full_track = '%s - %s' % (artist, track)
                if not full_track in tracks:
                    tracks.append(full_track)
        return tracks

    def parse(self, library_file):
        """
        Process Shazam downloadble playlist, return items
        """
        tracks = []
        with open(library_file, 'rb') as html_file:
            data = html_file.read()
            data = data.decode()
            tracks = self.html_parser(data)
        return tracks
