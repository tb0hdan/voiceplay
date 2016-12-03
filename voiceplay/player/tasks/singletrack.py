import re
from .basetask import BasePlayerTask


class SingleTrackArtistTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = ['^play (.+) bu?(?:t|y) (.+)$']
    __priority__ = 70
    __actiontype__ = 'single_track_artist'

    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, 'SingleTrackArtistTask')
        track, artist = re.match(regexp, message).groups()
        cls.play_full_track('%s - %s' % (artist, track))
