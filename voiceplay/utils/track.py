#-*- coding: utf-8 -*-
""" VoicePlay track handling module """

import re

from voiceplay.database import voiceplaydb

class TrackNormalizer(object):
    """
    Normalize tracks, check their status, etc
    """
    keywords = ['karaoke', 'djfm toronto ids', 'djfm ids', 'djfm ottawa', '@paulburyradio']

    @classmethod
    def track_ok(cls, track):
        """
        Track name doesn't have blacklisted keywords
        """
        status = True
        for keyword in cls.keywords:
            if keyword in track.lower():
                status = False
                break
        return status

    @classmethod
    def normalize(cls, trackname):
        """
        Normalize track names, mostly required for online radio
        TODO: move this out to json
        """
        # djfm.ca
        match = re.match('^Title:(.+)Artist:(.+)$', trackname)
        if match:
            artist = ' '.join([w.capitalize() for w in match.groups()[1].lower().split(' ')])
            title = ' '.join([w.capitalize() for w in match.groups()[0].lower().split(' ')])
            trackname = u'{0!s} - {1!s}'.format(artist.strip(), title.strip())
        # radioRoks
        match = re.match(r'^@\s(?:Rock|Made)(?:.+)\:\s(.+)$', trackname)
        if match:
            trackname = match.groups()[0]
        return trackname

    def filter_tracks(cls, tracks):
        """
        Track filter, accepts list of tracks, returns those that are ok
        """
        return filter(cls.track_ok, tracks)

    @classmethod
    def is_locally_blacklisted(cls, track):
        """
        Check if track is in local blacklist
        """
        return voiceplaydb.get_track_status(track) == 'banned'


def normalize(trackname):
    """
    Normalize wrapper
    """
    return TrackNormalizer.normalize(trackname)

def track_ok(trackname):
    """
    Track_ok wrapper
    """
    return TrackNormalizer.track_ok(trackname)

def filter_tracks(tracks):
    """
    Track filter wrapper
    """
    return TrackNormalizer.filter_tracks(tracks)
