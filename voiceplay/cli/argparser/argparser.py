#-*- coding: utf-8 -*-
""" VoicePlay argument parser module """

import argparse
import os
import subprocess
import sys
import threading
from functools import cmp_to_key
from voiceplay import __version__, __title__
from voiceplay.recognition.vicki import Vicki
from voiceplay.recognition.wakeword.receiver import ThreadedRequestHandler, WakeWordReceiver
from voiceplay.cli.console.console import Console
from voiceplay.utils.loader import PluginLoader
from voiceplay.player.tasks.basetask import BasePlayerTask
from voiceplay.player.hooks.basehook import BasePlayerHook
from voiceplay.utils.helpers import purge_cache, ThreadGroup, cmp

class MyArgumentParser(object):
    """
    Parse command line arguments
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=__title__, prog=__title__)

    def configure(self):
        """
        Configure argument parser
        """
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-c', '--console', action='store_true', default=False,
                           dest='console',
                           help='Start console')
        group.add_argument('-cd', '--console-devel', action='store_true',
                           default=False, dest='console_devel',
                           help='Start development console')
        group.add_argument('-w', '--wakeword', action='store_true',
                           default=False, dest='wakeword',
                           help='Start wakeword listener')
        self.parser.add_argument('-V', '--version', action='version',
                                 version='%(prog)s ' +  __version__)
        self.parser.add_argument('-v', '--verbose', action='store_true',
                                 default=False,
                                 dest='debug',
                                 help='Enable debug mode')
        # configure args for plugins
        plugins = sorted(PluginLoader().find_classes('voiceplay.player.tasks', BasePlayerTask),
                         key=cmp_to_key(lambda x, y: cmp(x.__priority__, y.__priority__)))
        plugins += sorted(PluginLoader().find_classes('voiceplay.player.hooks', BasePlayerHook),
                         key=cmp_to_key(lambda x, y: cmp(x.__priority__, y.__priority__)))
        for plugin in plugins:
            try:
                attr = getattr(plugin, 'configure_argparser')
            except Exception as exc:
                attr = None
            if attr:
                plugin.configure_argparser(self.parser)



    @staticmethod
    def ipython_console():
        """
        Run ipython console
        """
        from traitlets.config import Config
        from IPython.terminal.embed import InteractiveShellEmbed
        config = Config()
        # basic configuration
        config.TerminalInteractiveShell.confirm_exit = False
        #
        embed = InteractiveShellEmbed(config=config, banner1='')
        embed.mainloop()

    @staticmethod
    def player_console(vicki):
        """
        Start VickiPlayer console
        """
        console = Console()
        console.add_handler('play', vicki.player.play_from_parser,
                            ['pause', 'shuffle', 'next', 'stop', 'resume'])
        console.add_handler('what', vicki.player.play_from_parser)
        console.run_console()

    def vicki_loop(self, vicki, noblock=False):
        """
        Run Vicki loop
        """
        vicki.player.start()
        vicki.tts.start()
        ThreadedRequestHandler.callback = vicki.wakeword_callback
        address = ('127.0.0.1', 63455)
        server = WakeWordReceiver(address,
                                      ThreadedRequestHandler)
        threads = ThreadGroup()
        threads.targets = [server.serve_forever]
        threads.start_all()
        vicki.run_forever_new(server, noblock=noblock)

    def wakeword_loop(self):
        """
        Run wakeword listener loop
        """
        thread = threading.Thread(target=subprocess.call, args=(['python', '-m', 'voiceplay.recognition.wakeword.sender'],))
        thread.start()

    def parse(self, argv=None, noblock=False):
        """
        Parse command line arguments
        """
        argv = sys.argv if not argv else argv
        result = self.parser.parse_args(argv[1:])
        vicki = Vicki(debug=result.debug)
        vicki.player.argparser = result
        if result.console:
            vicki.player.start()
            self.player_console(vicki)
            vicki.player.shutdown()
        elif result.wakeword:
            self.vicki_loop(vicki, noblock=True)
            self.wakeword_loop()
        elif result.console_devel:
            self.ipython_console()
        else:
            self.vicki_loop(vicki)
        purge_cache()
