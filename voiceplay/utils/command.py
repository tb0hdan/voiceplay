#-*- coding: utf-8 -*-
""" Command module """

class Command(object):
    """
    Contain known commands and make their use clear and unambiguous.
    """
    STOP = 'stop'
    NEXT = 'next'
    PLAY = 'play'
    PAUSE = 'pause'
    RESUME = 'resume'
    SHUFFLE = 'shuffle'
    SHUTDOWN = 'shutdown'
    SHUTDOWN_ALIASES = ['exit', 'logout', 'quit', 'shutdown']
    CLEAR = 'clear'
    CLEAR_ALIASES = ['cls', 'clr']
    COMMAND = None
    LOVE = 'love'
    LOVE_ALIASES = ['unban', 'love', 'like']
    BAN = 'ban'
    BAN_ALIASES = ['ban', 'hate', 'dislike']

    def __init__(self, message=None):
        self.command_sets = {self.STOP: ['stop', 'stock', 'top', 'cancel'],
                             self.NEXT: ['next', 'max', 'maxed', 'text'],
                             self.PAUSE: ['pause', 'boss'],
                             self.RESUME: ['resume'],
                             self.SHUFFLE: ['shuffle'],
                             self.SHUTDOWN: self.SHUTDOWN_ALIASES,
                             self.CLEAR: self.CLEAR_ALIASES,
                             self.LOVE: self.LOVE_ALIASES,
                             self.BAN: self.BAN_ALIASES
                            }
        self.CONTROLS = [self.PAUSE, self.SHUFFLE, self.NEXT, self.STOP, self.RESUME, self.LOVE, self.BAN]
        self.COMMAND = self.__parse(message=message)

    def __parse(self, message=None):
        """
        Parse player command
        """
        result = None
        if not message:
            return result
        message = message.strip().lower()
        for cmd_key in self.command_sets:
            values = self.command_sets[cmd_key]
            for value in values:
                if message == value or message.replace(' ', '') == value:
                    result = cmd_key
                    break
            if result:
                break
        return result

    @property
    def IN_ALL_SET(self):
        """
        Command is known
        """
        all_set = []
        for cmd_key in self.command_sets:
            all_set.append(cmd_key)
        return self.COMMAND in all_set
