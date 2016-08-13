import re
from .basetask import BasePlayerTask


class LocalLibraryTask(BasePlayerTask):

    __group__ = ['play', 'shuffle']
    __regexp__ = '^play (.+)?my library$'
    __priority__ = 50
    __actiontype__ = 'shuffle_local_library'

    @classmethod
    def play_local_library(cls, message):
        fnames = []
        library = os.path.expanduser('~/Music')
        for root, _, files in os.walk(library, topdown=False):
            for name in files:
                if name.lower().endswith('.mp3'):
                    fnames.append(os.path.join(root, name))
        random.shuffle(fnames)
        for fname in fnames:
            if cls.exit_task:
                break
            cls.player.play(fname)

    @classmethod
    def process(cls, message):
        msg = re.match(reg, action_phrase).groups()[0]
        logger.warning(msg)
        cls.play_local_library(msg)
