#-*- coding: utf-8 -*-
""" Wakeword receiver module """
import SocketServer as socketserver
import threading


class ThreadedRequestHandler(socketserver.BaseRequestHandler):
    callback = None
    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        if self.callback and callable(self.callback):
            self.callback(data)  # pylint:disable=not-callable
        cur_thread = threading.currentThread()
        response = b'%s: %s' % (cur_thread.getName(),
                                data)
        self.request.send(response)
        return


class WakeWordReceiver(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address=True
