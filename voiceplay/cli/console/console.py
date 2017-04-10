#-*- coding: utf-8 -*-
""" Console module container """

from __future__ import print_function

import sys
import time

from builtins import input

import colorama
import rl

from voiceplay import __title__
from voiceplay.utils.helpers import SingleQueueDispatcher
from voiceplay.utils.command import Command

class Console(object):
    """
    Console mode object
    """
    def __init__(self, banner='Welcome to {0} console!'.format(__title__)):
        self.name = __title__
        self.default_prompt = '%s [%s]%s '
        self.exit = False
        self.banner = banner
        self.commands = {}
        self.queue = None
        self.dispatcher = None

    def set_queue(self, queue=None):
        """
        Pass command queue
        """
        self.queue = queue

    def set_exit(self):
        """
        Set exit flag
        """
        self.exit = True
        if self.dispatcher:
            self.dispatcher.set_exit()

    def add_handler(self, keyword, method, aliases=None):
        """
        Adds command handler to console
        """
        aliases = aliases if aliases else []
        self.commands[keyword] = {'method': method, 'aliases': aliases}

    @property
    def format_prompt(self):
        """
        Format command line prompt
        """
        result = self.default_prompt % (time.strftime('%H:%M:%S'),
                                        colorama.Fore.GREEN + colorama.Style.BRIGHT + self.name + colorama.Style.RESET_ALL,
                                        colorama.Fore.CYAN + colorama.Style.BRIGHT + '>' + colorama.Style.RESET_ALL)
        return result

    def parse_command(self, command):
        """
        Parse entered command
        """
        result = None
        should_be_printed = True
        orig_command = command.strip()
        command = orig_command.lower()
        for kwd in self.commands:
            if command.startswith(kwd) or [c for c in self.commands[kwd]['aliases'] if command.startswith(c)]:
                try:
                    result, should_be_printed = self.commands[kwd]['method'](orig_command)
                    break
                except KeyboardInterrupt:
                    pass
        return result, should_be_printed

    def quit_command(self, _):
        """
        Handle quit / exit / logout command
        """
        self.exit = True
        result = None
        should_be_printed = False
        return result, should_be_printed

    @staticmethod
    def clear_command(_):
        """
        Handle clear command
        """
        sys.stderr.flush()
        sys.stderr.write("\x1b[2J\x1b[H")
        result = None
        should_be_printed = False
        return result, should_be_printed

    def complete(self, _, state):
        """
        Provide autocompletion support (buggy)
        """
        text = rl.readline.get_line_buffer()  # pylint:disable=no-member
        if not text:
            return [c + ' ' for c in self.commands][state]
        results = [c + ' ' for c in self.commands if c.startswith(text)]
        return results[state]

    @staticmethod
    def run_exit():
        """
        Finalize exit (invoked after self.quit_command)
        """
        print ('Goodbye!')

    def run_console(self):
        """
        Actual console runner
        """
        inp = None
        colorama.init()
        # FSCK! Details here: http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
        if 'libedit' in rl.readline.__doc__:  # pylint:disable=unsupported-membership-test
            rl.readline.parse_and_bind("bind ^I rl_complete")  # pylint:disable=no-member
        else:
            rl.readline.parse_and_bind("tab: complete")  # pylint:disable=no-member
        rl.readline.set_completer(self.complete)  # pylint:disable=no-member
        # Add handlers
        self.add_handler(Command.SHUTDOWN, self.quit_command, Command.SHUTDOWN_ALIASES)
        self.add_handler(Command.CLEAR, self.clear_command, Command.CLEAR_ALIASES)
        #
        if self.banner:
            print (self.banner)
        while True:
            print (self.format_prompt, end='')
            try:
                inp = input()
                if sys.version_info.major == 2:
                    inp = inp.decode('utf-8')
            except KeyboardInterrupt:
                pass
            except EOFError:
                self.exit = True
                inp = None
            if inp:
                result, should_be_printed = self.parse_command(inp)
                if should_be_printed:
                    print (result)
            if self.exit:
                self.run_exit()
                break

    def run_bg_queue(self):
        """
        Run API commands background queue poller
        """
        if not self.queue:
            return
        self.dispatcher = SingleQueueDispatcher(queue=self.queue)
        while not self.exit:
            full_message = self.dispatcher.get_full_message()
            message = full_message.get('message')
            uuid = full_message.get('uuid')
            if not message:
                time.sleep(0.1)
                continue
            # do last.fm style normalization, i.e. replace + with space
            message = message.replace('+', ' ')
            print (message)
            result, should_be_printed = self.parse_command(message)
            self.dispatcher.put_message(uuid, result)
            if should_be_printed:
                    print (result)
            time.sleep(0.1)
