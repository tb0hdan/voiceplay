#-*- coding: utf-8 -*-
""" VoicePlay argument parser module """

from __future__ import print_function

import argparse
import os
import multiprocessing
import subprocess
import sys
import threading

from functools import cmp_to_key

from voiceplay import __version__, __title__
from voiceplay.logger import logger
from voiceplay.recognition.vicki import Vicki
from voiceplay.recognition.wakeword.receiver import ThreadedRequestHandler, WakeWordReceiver
from voiceplay.cli.console.console import Console
from voiceplay.utils.loader import PluginLoader
from voiceplay.player.tasks.basetask import BasePlayerTask
from voiceplay.player.hooks.basehook import BasePlayerHook
from voiceplay.utils.helpers import purge_cache, ThreadGroup, cmp
from voiceplay.utils.models import BaseCfgModel
from voiceplay.config.configurator import ConfigDialog

class Help(object):
    help_aliases = ['?', 'h', 'help']
    def __init__(self):
        pass

    def run_help(self, *args, **kwargs):
        if args[0].strip() in self.help_aliases:
            return self.main_page(), True
        return None, False

    def main_page(self):
        message = """{0} {1}\nTo get help about {2} commands type:
\t"<tab>" to get a list of possible help topics
\t"clear" to clear screen
\t"quit" or press CTRL+D to exit\n
Set your preferences in ~/.config/voiceplay/config.yaml\n""".format(__title__, __version__, __title__)
        return message

    def register(self, console_obj):
        console_obj.add_handler('help', self.run_help, self.help_aliases)


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
        group.add_argument('-C', '--configure', action='store_true', default=False,
                           dest='configure',
                           help='Run configuration utility')
        group.add_argument('-c', '--console', action='store_true', default=False,
                           dest='console',
                           help='Start console')
        group.add_argument('-cd', '--console-devel', action='store_true',
                           default=False, dest='console_devel',
                           help='Start development console')
        group.add_argument('-w', '--wakeword', action='store_true',
                           default=False, dest='wakeword',
                           help='Start wakeword listener')
        self.parser.add_argument('-W', '--webapp', action='store_true',
                                 default=False, dest='webapp', help='Start web application')
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
    def player_console(vicki, queue=None):
        """
        Start VickiPlayer console
        """
        helper = Help()
        console = Console()
        console.add_handler('play', vicki.player.play_from_parser,
                            ['pause', 'shuffle', 'next', 'stop', 'resume'])
        console.add_handler('what', vicki.player.play_from_parser)
        helper.register(console)
        console.set_queue(queue)
        th = ThreadGroup()
        th.targets = [console.run_bg_queue]
        th.start_all()
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

    def webapp_loop(self, debug=False, queue=None):
        """
        Run wakeword listener loop
        """
        from voiceplay.webapp import WrapperApplication
        app = WrapperApplication()
        app.debug = debug
        p = multiprocessing.Process(target=app.run, args=(queue,))
        p.start()
        return p


    def parse(self, argv=None, noblock=False):
        """
        Parse command line arguments
        """
        argv = sys.argv if not argv else argv
        result = self.parser.parse_args(argv[1:])
        # allow --configure
        if result.configure:
            cd = ConfigDialog()
            cd.run('~/.config/voiceplay/config.yaml')
            return
        # Check config here
        try:
            cfg_data = BaseCfgModel.cfg_data()
        except Exception as _:
            print('Configuration not found, please run {0!s} --configure'.format(__title__.lower()))
            return
        #
        vicki = Vicki(debug=result.debug)
        vicki.player.player.set_argparser(result)
        proc = None
        queue = multiprocessing.Queue()
        if result.webapp:
            # non-blocking
            proc = self.webapp_loop(debug=result.debug, queue=queue)
        if result.console:
            vicki.player.start()
            self.player_console(vicki, queue=queue)
            vicki.player.shutdown()
        elif result.wakeword:
            self.vicki_loop(vicki, noblock=True)
            self.wakeword_loop()
        elif result.console_devel:
            self.ipython_console()
        else:
            self.vicki_loop(vicki)
        if proc:
            proc.terminate()
        purge_cache()
