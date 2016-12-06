#-*- coding: utf-8 -*-

import SocketServer as socketserver
import threading

class ThreadedRequestHandler(socketserver.BaseRequestHandler):
    callback = None
    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        if self.callback:
            self.callback(data)
        cur_thread = threading.currentThread()
        response = b'%s: %s' % (cur_thread.getName().encode(),
                                data)
        self.request.send(response)
        return


class WakeWordReceiver(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address=True
