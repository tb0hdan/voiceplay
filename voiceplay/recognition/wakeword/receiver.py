#-*- coding: utf-8 -*-
""" Wakeword receiver module """

# works if `future` package is installed
import socketserver  # pylint:disable=no-name-in-module,import-error


class ThreadedRequestHandler(socketserver.BaseRequestHandler):
    """
    Wakeword request handler
    """
    callback = None
    def handle(self):
        """
        Handle socket message
        """
        # Echo the back to the client
        data = self.request.recv(1024)
        if self.callback and callable(self.callback):
            self.callback(data)  # pylint:disable=not-callable
        response = b'Ok'
        self.request.send(response)
        return


class WakeWordReceiver(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Wakeword receiver mixin class
    """
    allow_reuse_address = True
