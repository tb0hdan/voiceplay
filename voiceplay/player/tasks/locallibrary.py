class LocalLibraryTask(BasePlayerTask):

    __group__ = ['play', 'shuffle']
    __regexp__ = 
    __actiontype__ = 

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
