#-*- coding: utf-8 -*-
""" ASX playlist module """

from lxml import etree

class ASXFileLibrary(object):
    '''
    ASX playlist support
    '''
    @staticmethod
    def etree_parser(tree):
        """
        ASX (XML) parser using ElementTree
        """
        tracks = []
        for element in tree.iter():
            if element.tag != 'entry':
                continue
            for el in element.iter():
                if el.tag == 'title':
                    tracks.append(el.text)
        result = [chunk for chunk in [t for t in tracks if t]]
        return result

    def parse(self, library_file):
        """
        Process ASX playlist, return items
        """
        result = None
        with open(library_file, 'rb') as xml_file:
            tree = etree.parse(xml_file)
            result = self.etree_parser(tree)
        return result
