from __future__ import print_function

import colorama
import rl
import sys
import time

from voiceplay import __title__

class Console(object):
    '''
    Console mode
    '''
    def __init__(self, banner='Welcome to {0} console!'.format(__title__)):
        self.name = __title__
        self.default_prompt = '%s [%s]%s '
        self.exit = False
        self.banner = banner
        self.commands = {}

    def add_handler(self, keyword, method, aliases=None):
        '''
        Adds command handler to console
        '''
        aliases = aliases if aliases else []
        self.commands[keyword] = {'method': method, 'aliases': aliases}

    @property
    def format_prompt(self):
        '''
        Format command line prompt
        '''
        result = self.default_prompt % (time.strftime('%H:%M:%S'),
                                        colorama.Fore.GREEN + colorama.Style.BRIGHT + self.name + colorama.Style.RESET_ALL,
                                        colorama.Fore.CYAN + colorama.Style.BRIGHT + '>' + colorama.Style.RESET_ALL)
        return result

    def parse_command(self, command):
        '''
        Parse entered command
        '''
        result = None
        should_be_printed = True
        command = command.strip().lower()
        for kwd in self.commands:
            if command.startswith(kwd) or [c for c in self.commands[kwd]['aliases'] if command.startswith(c)]:
                try:
                    result, should_be_printed = self.commands[kwd]['method'](command)
                    break
                except KeyboardInterrupt:
                    pass
        return result, should_be_printed

    def quit_command(self, _):
        '''
        Handle quit / exit / logout command
        '''
        self.exit = True
        result = None
        should_be_printed = False
        return result, should_be_printed

    @staticmethod
    def clear_command(_):
        '''
        Handle clear command
        '''
        sys.stderr.flush()
        sys.stderr.write("\x1b[2J\x1b[H")
        result = None
        should_be_printed = False
        return result, should_be_printed

    def complete(self, _, state):
        '''
        Provide autocompletion support (buggy)
        '''
        text = rl.readline.get_line_buffer()
        if not text:
            return [c + ' ' for c in self.commands][state]
        results = [c + ' ' for c in self.commands if c.startswith(text)]
        return results[state]

    @staticmethod
    def run_exit():
        '''
        Finalize exit (invoked after self.quit_command)
        '''
        print ('Goodbye!')

    def run_console(self):
        inp = None
        colorama.init()
        # FSCK! Details here: http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
        if 'libedit' in rl.readline.__doc__:
            rl.readline.parse_and_bind("bind ^I rl_complete")
        else:
            rl.readline.parse_and_bind("tab: complete")
        rl.readline.set_completer(self.complete)
        # Add handlers
        self.add_handler('quit', self.quit_command, ['exit', 'logout'])
        self.add_handler('clear', self.clear_command, ['cls', 'clr'])
        #
        if self.banner:
            print (self.banner)
        while True:
            print (self.format_prompt, end='')
            try:
                inp = raw_input()
                if sys.version_info.major == 2:
                    inp = inp.decode('utf-8')
            except KeyboardInterrupt:
                pass
            except EOFError:
                self.exit = True
                inp = None
            if inp:
                result, should_be_printed = self.parse_command(inp)
            if self.exit:
                self.run_exit()
                break
