#-*- coding: utf-8 -*-
""" VoicePlay CLI module """

from voiceplay.logger import logger
from voiceplay.utils.updatecheck import check_update
from .argparser.argparser import MyArgumentParser


def main(noblock=False):
    """
    CLI Main, called from shell script

    :param noblock: Disable server thread lock-up, requires extra care to run
    :type noblock: bool
    """
    message = check_update(suppress_uptodate=True)
    if message:
        logger.error(message)
    parser = MyArgumentParser()
    parser.configure()
    parser.parse(noblock=noblock)

if __name__ == '__main__':
    main()
