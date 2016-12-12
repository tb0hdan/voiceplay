import re

class TrackNormalizer(object):
    """
    """
    @classmethod
    def normalize(cls, trackname):
        # djfm.ca
        match = re.match('^Title:(.+)Artist:(.+)$', trackname)
        if match:
            artist = ' '.join([w.capitalize() for w in match.groups()[1].lower().split(' ')])
            title = ' '.join([w.capitalize() for w in match.groups()[0].lower().split(' ')])
            trackname = '{0!s} - {1!s}'.format(artist.strip(), title.strip())
        return trackname


def normalize(trackname):
    return TrackNormalizer.normalize(trackname)
