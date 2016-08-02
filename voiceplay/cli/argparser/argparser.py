import argparse
import threading
import sys
from voiceplay import __version__, __title__
from voiceplay.recognition.vicki import Vicki
from voiceplay.recognition.wakeword.receiver import ThreadedRequestHandler, WakeWordReceiver
from voiceplay.cli.console.console import Console

class MyArgumentParser(object):
    '''
    Parse command line arguments
    '''
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='VoicePlay', prog=__title__)

    def configure(self):
        '''
        Configure argument parser
        '''
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-c', '--console', action='store_true', default=False, dest='console',
                           help='Start console')
        group.add_argument('-cd', '--console-devel', action='store_true', default=False, dest='console_devel',
                           help='Start development console')
        self.parser.add_argument('-V', '--version', action='version', version='%(prog)s ' +  __version__)
        self.parser.add_argument('-v', '--verbose', action='store_true', default=False, 
                                dest='debug',
                                help='Enable debug mode')

    @staticmethod
    def ipython_console():
        '''
        Run ipython console
        '''
        from traitlets.config import Config
        from IPython.terminal.embed import InteractiveShellEmbed
        config = Config()
        # basic configuration
        config.TerminalInteractiveShell.confirm_exit = False
        #
        embed = InteractiveShellEmbed(config=config, banner1='')
        embed.mainloop()

    def player_console(self, vicki):
        console = Console()
        console.add_handler('play', vicki.player.play_from_parser, ['pause', 'shuffle', 'next', 'stop', 'resume'])
        console.add_handler('what', vicki.player.play_from_parser)
        console.run_console()

    def parse(self, argv=None):
        '''
        Parse command line arguments
        '''
        argv = sys.argv if not argv else argv
        result = self.parser.parse_args(argv[1:])
        vicki = Vicki(debug=result.debug)
        if result.console:
            vicki.player.start()
            self.player_console(vicki)
            vicki.player.shutdown()
        elif result.console_devel:
            self.ipython_console()
        else:
            vicki.player.start()
            ThreadedRequestHandler.callback = vicki.wakeword_callback
            address = ('127.0.0.1', 63455)
            server = WakeWordReceiver(address,
                                ThreadedRequestHandler)
            t = threading.Thread(target=server.serve_forever)
            t.setDaemon(True)
            t.start()
            vicki.run_forever_new()
