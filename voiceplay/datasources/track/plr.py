from .tracksource import TrackSource

class PleerSource(TrackSource):
    def search(self, query, max_results=25):
        term = quote(query)
        url = 'http://pleer.net/search?page=1&q=%s&sort_mode=0&sort_by=0&quality=all&onlydata=true' % quote(query)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.net/search?q=%s' % term}
        r = requests.get(url, headers=headers, timeout=10)
        result = json.loads(r.text).get('html', '')
        soup = BeautifulSoup(''.join(result), 'html.parser')
        tracks = []
        for el in soup.findAll(lambda tag: tag.name == 'div' and tag.a and tag.a['href'] == '#'):
            tg = el.findParent()
            if not tg.name == 'li':
                continue
            title = '%s - %s' % (tg.get('singer'), tg.get('song'))
            aid = tg.get('link')
            tracks.append([title, aid])
        return tracks

    def download(self, track_url, filename, chunk_size=8196):
        '''
        Download track
        '''
        track_id = track_url.replace('http://pleer.net/en/download/page/', '')
        url = 'http://pleer.net/site_api/files/get_url'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.net/en/download/page/%s' % track_id}
        reply = requests.post(url, data={'action': 'download', 'id': track_id}, timeout=10)
        result = json.loads(reply.text).get('track_link')
        r = requests.get(result, headers=headers, stream=True, timeout=10)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
