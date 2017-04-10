#-*- coding: utf-8 -*-
""" Playlist guesser module """

from ..libraries import (iTunesLibrary,
                         ShazamDownloadLibrary,
                         TextFileLibrary,
                         PLSFileLibrary,
                         M3UFileLibrary,
                         ASXFileLibrary)

def library_guesser(filename, url_only=False):
    """
    Playlist type guesser
    File only mode so far
    """
    result = None
    if filename:
        if filename.lower().endswith('.xml'):
            library = iTunesLibrary()
        elif filename.lower().endswith('.html'):
            library = ShazamDownloadLibrary()
        elif filename.lower().endswith('.txt'):
            library = TextFileLibrary()
        elif filename.lower().endswith('.pls'):
            library = PLSFileLibrary()
        elif filename.lower().endswith('.m3u'):
            library = M3UFileLibrary()
        elif filename.lower().endswith('.asx'):
            library = ASXFileLibrary()
        else:
            return result
        result = library.parse(filename, url_only=url_only)
    return result
