class Console(object):
    '''
    Console mode
    '''
    def __init__(self, banner='Welcome to voiceplay console!'):
        self.name = 'voiceplay'
        self.default_prompt = '%s [%s]%s '
        self.exit = False
        self.banner = banner
        self.commands = {}

    def add_handler(self, keyword, method, aliases=None):
        aliases = aliases if aliases else []
        self.commands[keyword] = {'method': method, 'aliases': aliases}

    @property
    def format_prompt(self):
        result = self.default_prompt % (time.strftime('%H:%M:%S'),
                                        colorama.Fore.GREEN + colorama.Style.BRIGHT + self.name + colorama.Style.RESET_ALL,
                                        colorama.Fore.CYAN + colorama.Style.BRIGHT + '>' + colorama.Style.RESET_ALL)
        return result

    def parse_command(self, command):
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

    def quit_command(self, cmd):
        self.exit = True
        result = None
        should_be_printed = False
        return result, should_be_printed

    def clear_command(self, cmd):
        sys.stderr.flush()
        sys.stderr.write("\x1b[2J\x1b[H")
        result = None
        should_be_printed = False
        return result, should_be_printed

    def complete(self, _, state):
        text = readline.get_line_buffer()
        if not text:
            return [c + ' ' for c in self.commands][state]
        results = [c + ' ' for c in self.commands if c.startswith(text)]
        return results[state]

    def run_exit(self):
        print ('Goodbye!')

    def run_console(self):
        inp = None
        colorama.init()
        # FSCK! Details here: http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete)
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
