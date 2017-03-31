#-*- coding: utf-8 -*-
""" Basic MusicBrainz API wrapper """

import musicbrainzngs

from voiceplay import (__title__,
                       __version__,
                       __website__)

class MBAPI(object):
    """
    MusicBrainz API
    """
    def __init__(self):
        musicbrainzngs.set_useragent(__title__,
                                     __version__,
                                     __website__)
    @classmethod
    def get_artist_mbid(cls, artist):
        """
        Get artist musicbrainz ID

        @param: Artist name
        """
        result = musicbrainzngs.search_artists(artist=artist)
        mbid = None
        for artist in result.get('artist-list', []):
            score = int(artist.get('ext:score', 0))
            if score == 100:
                mbid = artist.get('id', None)
                break
        return mbid

    @classmethod
    def get_artist_names(cls, artist):
        """
        @param: Artist name
        @return: list of similar names
        """
        result = musicbrainzngs.search_artists(artist=artist)
        alist = []
        for artist in result.get('artist-list', []):
            name = artist.get('name', None)
            if name and not name in alist:
                alist.append(name)
        return alist

    @classmethod
    def get_releases(cls, mbid, rtypes=None):
        """
        @param: Artist mbid
        """
        limit = 100
        rtypes = ['album'] if not rtypes else rtypes
        result = musicbrainzngs.browse_releases(artist=mbid,
                                                release_type=rtypes,
                                                limit=limit)
        page_releases = result['release-list']
        albums = []
        known_titles = []
        for release in page_releases:
            if release.get('status', '') == 'Official':
                mbid = release.get('id', '')
                date = release.get('date', '')
                date = date.split('-')[0]
                title = release.get('title', '')
                if title and not title in known_titles:
                    known_titles.append(title)
                    albums.append({'title': title, 'mbid': mbid, 'date': date})
        return albums

    @classmethod
    def get_recordings(cls, mbid):
        """
        @param: Release mbid
        """
        result = musicbrainzngs.browse_recordings(release=mbid, limit=100)
        tracks = result.get('recording-list', [])
        return tracks
