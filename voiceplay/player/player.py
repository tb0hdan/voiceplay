import os
import subprocess
import threading

class ConsolePlayer(object):
    '''
    Console player
    '''
    def __init__(self, *args, **kwargs):
        self.lock = threading.Lock()
        self.stdout_pool = []
        self.stderr_pool = []

    def player_stdout_thread(self):
        while self.proc.poll() is None:
            line = self.proc.stdout.readline().rstrip('\n')
            if line:
                self.stdout_pool.append(line.strip())

    def player_stderr_thread(self):
        while self.proc.poll() is None:
            line = self.proc.stderr.readline().rstrip('\n')
            if line:
                self.stderr_pool.append(line.strip())

    def send_command(self, command):
        with self.lock:
            self.proc.stdin.write(command + '\n')

    def stop(self):
        try:
            os.killpg(self.proc.pid, signal.SIGTERM)
        except OSError:
            pass
        self.stdout_thread.join()
        self.stderr_thread.join()

    def start(self):
        self.proc = subprocess.Popen(self.command,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     close_fds=True,
                                     preexec_fn=os.setsid)

        self.stdout_thread = threading.Thread(name='player_stdout', target=self.player_stdout_thread)
        self.stdout_thread.setDaemon(True)
        self.stdout_thread.start()

        self.stderr_thread = threading.Thread(name='player_stderr', target=self.player_stderr_thread)
        self.stderr_thread.setDaemon(True)
        self.stderr_thread.start()


class MPlayerSlave(ConsolePlayer):
    '''
    MPlayer slave
    '''
    def __init__(self, *args, **kwargs):
        self.command = ['mplayer', '-slave', '-idle',
               '-really-quiet', '-msglevel', 'global=6:cplayer=4', '-msgmodule',
               '-vo', 'null', '-cache', '1024']
        super(MPlayerSlave, self).__init__(*args, **kwargs)
        self._state = 'started'

    def play(self, uri, block=True):
        cmd = 'loadfile %s' % uri
        self.send_command(cmd.encode('utf-8'))
        if block:
            while self.state != 'stopped':
                time.sleep(0.5)

    def stop_playback(self):
        if self._state in ['playing', 'paused']:
            self.send_command('stop')
            self._state = 'stopped'

    def pause(self):
        if self._state == 'playing':
            self.send_command('pause')
            self._state = 'paused'

    def resume(self):
        if self._state == 'paused':
            self.send_command('pause')
            self._state = 'playing'

    def shutdown(self):
        self.send_command('quit')
        time.sleep(0.5)
        self.stop()

    def get_state(self):
        for line in self.stdout_pool:
            if line.startswith('GLOBAL: EOF code'):
                self._state = 'stopped'
                break
            if line.startswith('CPLAYER: Starting playback'):
                self._state = 'playing'
                break
        self.stdout_pool = []
        self.stderr_pool = []

    @property
    def state(self):
        self.get_state()
        return self._state
