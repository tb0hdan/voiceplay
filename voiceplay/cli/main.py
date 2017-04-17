#-*- coding: utf-8 -*-
""" VoicePlay CLI module """

import sys

from voiceplay.logger import logger
from voiceplay.utils.updatecheck import check_update
from voiceplay.utils.crashlog import send_traceback
from voiceplay.utils.helpers import SignalHandler
from .argparser.argparser import MyArgumentParser


def main(noblock=False):
    """
    CLI Main, called from shell script

    :param noblock: Disable server thread lock-up, requires extra care to run
    :type noblock: bool
    """
    signal_handler = SignalHandler()
    signal_handler.register()
    message = check_update(suppress_uptodate=True)
    if message:
        logger.error(message)
    parser = MyArgumentParser(signal_handler=signal_handler)
    parser.configure()
    try:
        parser.parse(noblock=noblock)
    except Exception as _:
        send_traceback(sys.exc_info(), __file__)

if __name__ == '__main__':
    main()
