#-*- coding: utf-8 -*-
""" Wakeword receiver module """
import sys
if sys.version_info.major == 2:
    import SocketServer as socketserver  # pylint:disable=no-name-in-module,import-error
elif sys.version_info.major == 3:
    import socketserver  # pylint:disable=no-name-in-module,import-error

import threading


class ThreadedRequestHandler(socketserver.BaseRequestHandler):
    callback = None
    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        if self.callback and callable(self.callback):
            self.callback(data)  # pylint:disable=not-callable
        cur_thread = threading.currentThread()
        response = b'Ok'
        #'%s: %s' % (cur_thread.getName(),
        #                        data)
        self.request.send(response)
        return


class WakeWordReceiver(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address=True
