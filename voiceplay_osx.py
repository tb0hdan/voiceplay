#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import multiprocessing
import sys

import rumps
rumps.debug_mode(True)


from voiceplay import __title__ as vp_title
from voiceplay.cli.argparser.argparser import MyArgumentParser, Help
from voiceplay.logger import logger
from voiceplay.utils.updatecheck import check_update
from voiceplay.utils.crashlog import send_traceback
from voiceplay.utils.helpers import SignalHandler
from voiceplay.recognition.vicki import Vicki

from voiceplay.cli.console.console import Console
from voiceplay.utils.command import Command
from voiceplay.utils.helpers import ThreadGroup, cmp


class VoicePlayApp(rumps.App):
    def __init__(self):
        super(VoicePlayApp, self).__init__(vp_title, quit_button=None)
        self.menu = ['Pause/Resume', 'Quit']

    @rumps.clicked('Pause/Resume')
    def pause_resume(self, _):
        try:
            self.console.parse_command('pause')
        except Exception as exc:
            logger.error(repr(exc))

    @rumps.clicked('Quit')
    def menu_quit(self, _):
        try:
            self.console.set_exit()
            self.vicki.player.shutdown()
            self.th.stop_all()
        except Exception as exc:
            logger.error(repr(exc))
        rumps.quit_application()

    def player_console(self, vicki, queue=None):
        """
        Start VickiPlayer console
        """
        helper = Help()
        #self.console = Console()
        self.console.add_handler(Command.PLAY, vicki.player.play_from_parser, Command().CONTROLS)
        self.console.add_handler('what', vicki.player.play_from_parser)
        self.console.add_handler('current_track', vicki.player.play_from_parser)
        helper.register(self.console)
        self.console.set_queue(queue)
        th = ThreadGroup(restart=False)
        th.targets = [self.console.run_bg_queue]
        th.start_all()
        self.console.run_console()
        self.console.set_exit()
        th.stop_all()

    def __run_console__(self):
        self.parser.player_console(self.vicki, queue=self.queue)

    def __run_bg__(self):
        self.th = ThreadGroup(restart=False)
        self.th.targets = [self.__run_console__]
        self.th.start_all()

    def run_app(self):
        signal_handler = SignalHandler()
        signal_handler.register()
        message = check_update(suppress_uptodate=True)
        if message:
            logger.error(message)
        parser = MyArgumentParser(signal_handler=signal_handler)
        parser.configure()
        # first parse is just for debug
        result = parser.parser.parse_args(sys.argv[1:])
        debug = result.debug
        #
        rumps.debug_mode(debug)
        #
        result = parser.parser.parse_args(['-c'])
        vicki = Vicki(debug=debug, player_backend=result.player_backend)
        vicki.player.player.set_argparser(result)
        #
        self.console = Console()
        #
        self.queue = multiprocessing.Queue()
        vicki.player.start()
        self.vicki = vicki
        self.parser = parser
        self.__run_bg__()
        self.run()

if __name__ == '__main__':
    VoicePlayApp().run_app()
