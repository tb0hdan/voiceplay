#-*- coding: utf-8 -*-
""" Plaintext playlist module """


class TextFileLibrary(object):
    """
    (not) Very basic and silly TXT parser
    """
    def __init__(self):
        self.checks = [lambda x: x.startswith('#'), lambda x: x.startswith('//'),
                       lambda x: x.startswith('/*')]

    def line_ok(self, line):
        """
        Confirm that line is okay by honoring comments
        """
        status = True
        for check in self.checks:
            if check(line):
                status = False
                break
        return status

    def text_parser(self, data):
        """
        .txt file parser
        """
        tracks = []
        for line in data.splitlines():
            track = line.strip()
            if not self.line_ok(track):
                continue
            tracks.append(track)
        return tracks

    def parse(self, library_file):
        """
        Process TXT playlist, return items
        """
        tracks = []
        with open(library_file, 'rb') as text_file:
            data = text_file.read()
            data = data.decode()
            tracks = self.text_parser(data)
        return tracks
