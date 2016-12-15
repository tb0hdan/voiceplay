import re

class TrackNormalizer(object):
    """
    """
    keywords = ['remix', 'karaoke']

    @classmethod
    def track_ok(cls, track):
        status = True
        for keyword in cls.keywords:
            if keyword in track.lower():
                status = False
                break
        return status

    @classmethod
    def normalize(cls, trackname):
        # djfm.ca
        match = re.match('^Title:(.+)Artist:(.+)$', trackname)
        if match:
            artist = ' '.join([w.capitalize() for w in match.groups()[1].lower().split(' ')])
            title = ' '.join([w.capitalize() for w in match.groups()[0].lower().split(' ')])
            trackname = u'{0!s} - {1!s}'.format(artist.strip(), title.strip())
        # radioRoks
        match = re.match('^@\s(?:Rock|Made)(?:.+)\:\s(.+)$', trackname)
        if match:
            trackname = match.groups()[0]
        return trackname

    def filter_tracks(cls, tracks):
        return filter(cls.track_ok, tracks)

def normalize(trackname):
    return TrackNormalizer.normalize(trackname)

def filter_tracks(tracks):
    return TrackNormalizer.filter_tracks(tracks)
