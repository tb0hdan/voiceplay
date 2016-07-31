from .tracksource import TrackSource

class VimeoSource(TrackSource):
    __baseurl__ = 'https://vimeo.com/'
    __priority__ = 20

    @classmethod
    def search(cls, query, max_results=25):
        '''
        Run vimeo search
        '''
        client = vimeo.VimeoClient(token=cls.cfg_data['vimeo']['token'],
                                   key=cls.cfg_data['vimeo']['key'],
                                   secret=cls.cfg_data['vimeo']['secret'])
        response = client.get('/videos?query=%s' % quote(query))
        result = json.loads(response.text).get('data', [])
        videos = []
        for video in result:
            vid = video.get('uri', '').split('/videos/')[1]
            title = video.get('name', '')
            if not title.lower().startswith(query.lower()):
                continue
            videos.append([title, vid])
        return videos
