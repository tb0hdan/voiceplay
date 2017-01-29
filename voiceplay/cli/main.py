#-*- coding: utf-8 -*-
""" VoicePlay CLI module """

from .argparser.argparser import MyArgumentParser


def main(noblock=False):
    """
    CLI Main, called from shell script

    :param noblock: Disable server thread lock-up, requires extra care to run
    :type noblock: bool
    """
    parser = MyArgumentParser()
    parser.configure()
    parser.parse(noblock=noblock)

if __name__ == '__main__':
    main()
