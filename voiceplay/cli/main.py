#-*- coding: utf-8 -*-
''' VoicePlay CLI module '''

from .argparser.argparser import MyArgumentParser

def main(noblock=False):
    '''
    CLI Main, called from shell script
    '''
    parser = MyArgumentParser()
    parser.configure()
    parser.parse()

if __name__ == '__main__':
    main()
