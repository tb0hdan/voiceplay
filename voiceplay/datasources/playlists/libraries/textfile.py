#-*- coding: utf-8 -*-

class TextFileLibrary(object):
    '''
    (not that) Very basic and silly TXT parser
    '''
    def __init__(self):
        self.checks = [lambda x: x.startswith('#'), lambda x: x.startswith('//'),
                       lambda x: x.startswith('/*')]

    def line_ok(self, line):
        status = True
        for check in self.checks:
            if check(line):
                status = False
                break
        return status

    def text_parser(self, data):
        tracks = []
        for line in data.splitlines():
            track = line.strip()
            if not self.line_ok(track):
                continue
            tracks.append(track)
        return tracks

    def parse(self, library_file):
        tracks = []
        with open(library_file, 'rb') as text_file:
            data = text_file.read()
            data = data.decode()
            tracks = self.text_parser(data)
        return tracks
