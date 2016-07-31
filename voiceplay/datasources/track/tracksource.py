class TrackSource(object):
    '''
    '''
    @classmethod
    def search(cls, *args, **kwargs):
        raise NotImplementedError('{0} {1}'.format(cls.__name__, 'does not provide search method'))


    @classmethod
    def download(cls, track_url, filename):
        tmp = mkdtemp()
        template = os.path.join(tmp, '%(title)s-%(id)s.%(ext)s')
        ydl_opts = {'keepvideo': False, 'verbose': False, 'format': 'bestaudio/best',
                    'quiet': True, 'outtmpl': template,
                    'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '5',
                                        'nopostoverwrites': True, 'key': 'FFmpegExtractAudio'}],
                    'logger': logger,
                    'progress_hooks': [self.download_hook]}

        logger.warning('Using source url %s', url)
        if url.startswith('http://pleer.net/en/download/page/'):
            audio_file = mkstemp()[1]
            self.pleer_download(url, audio_file)
        else:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                audio_file = re.sub('\.(.+)$', '.mp3', self.target_filename)
        return target_filename
