from voiceplay.config import Config

class TrackSource(object):
    '''
    '''
    cfg_data = Config.cfg_data

    @classmethod
    def search(cls, *args, **kwargs):
        raise NotImplementedError('{0} {1}'.format(cls.__name__, 'does not provide search method'))


    @classmethod
    def download(cls, track_url, hooks=None):
        tmp = mkdtemp()
        template = os.path.join(tmp, '%(title)s-%(id)s.%(ext)s')
        ydl_opts = {'keepvideo': False, 'verbose': False, 'format': 'bestaudio/best',
                    'quiet': True, 'outtmpl': template,
                    'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '5',
                                        'nopostoverwrites': True, 'key': 'FFmpegExtractAudio'}],
                    'logger': logger}
        if hooks:
            ydl_opts['progress_hooks'] = hooks

        logger.warning('Using source url %s', url)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            audio_file = re.sub('\.(.+)$', '.mp3', cls.target_filename)
        return audio_file
