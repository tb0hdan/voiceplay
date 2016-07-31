from .tracksource import TrackSource

class DailyMotionSource(TrackSource):
    __baseurl__ = 'http://www.dailymotion.com/video/'
    __priority__ = 30

    def search(cls, query, max_results=25):
        '''
        Run dailymotion search
        '''
        maxresults = 100
        client = Dailymotion()
        client.set_grant_type('password',
                              api_key=cls.cfg_data['dailymotion']['key'],
                              api_secret=cls.cfg_data['dailymotion']['secret'],
                              info={'username': cls.cfg_data['dailymotion']['username'],
                                    'password': cls.cfg_data['dailymotion']['password']},
                              scope=['userinfo'])
        results = []
        pages = trunc(max_results/maxresults)
        pages = pages if pages > 0 else 1
        dquery = {'search': query,
                  'fields':'id,title',
                  'limit': maxresults}
        i = 0
        while i < pages:
            response = client.get('/videos', dquery)
            results += response.get('list', [])
            i += 1
            if not response.get('has_more', False):
                break
        videos = []
        for result in results:
            vid = result.get('id')
            title = result.get('title')
            if not title.lower().startswith(query.lower()):
                continue
            videos.append([title, vid])
        return videos
