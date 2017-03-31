#-*- coding: utf-8 -*-

from lxml import etree

class iTunesLibrary(object):
    '''
    iTunes library import
    '''
    @staticmethod
    def etree_parser(tree):
        tmp = {}
        tracks = []
        for element in tree.iter():
            if element.text in ['Name', 'Artist', 'Album', 'Genre']:
                if not tmp.get(element.text):
                    tmp[element.text] = element.getnext().text
                else:
                    tracks.append(tmp)
                    tmp = {}
        result = [chunk for chunk in [x for x in tracks if x.get('Artist', None)]]
        return result

    @staticmethod
    def normalizer(tracks):
        result = []
        for track in tracks:
            result.append('%s - %s' % (track.get('Artist', ''), track.get('Name', '')))
        return result

    def parse(self, library_file):
        '''
        '''
        result = None
        with open(library_file, 'rb') as xml_file:
            tree = etree.parse(xml_file)
            tracks = self.etree_parser(tree)
            result = self.normalizer(tracks)
        return result


if __name__ == '__main__':
    library = iTunesLibrary()
    tracks = library.parse('./Library.xml')
    if tracks:
        print (tracks)
