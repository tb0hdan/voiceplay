#-*- coding: utf-8 -*-
""" Helper functions / methods / classes """

import os
import signal
import sys
import threading
import time
import traceback

from builtins import input

from uuid import uuid4


from voiceplay.logger import logger

from .crashlog import send_traceback

class Singleton(type):
    """
    Singleton base class
    """
    cls_instances = {}
    def __call__(cls, *args, **kwargs):
        """
        Handle instantiation
        """
        if cls not in cls.cls_instances:
            cls.cls_instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.cls_instances[cls]


def debug_traceback(exc_info, fname, include_traceback=True, message=None):
    """
    Get full traceback, show if debugging is enabled
    """
    typ, value, tb = exc_info
    trace = ''.join(traceback.format_exception(typ, value, tb))
    message = 'Method crashed (see message below), restarting...' if not message else message
    if include_traceback:
        message += '\n\n%s\n' % trace
    send_traceback(exc_info, fname)
    logger.debug(message)


def restart_on_crash(method, *args, **kwargs):
    """
    Restart method on crash helper
    """
    while True:
        result = None
        try:
            result = method(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as _:
            debug_traceback(sys.exc_info(), __file__)
            # allow interrupt
            time.sleep(1)
        else:
            break
    logger.debug('Method %r completed without exception', method)
    return result


def run_hooks(argparser, hooks, evt, *args, **kwargs):
    """
    Run hooks (player/recognition/etc)
    """
    for hook in hooks:
        logger.debug('Running hook: %r', hook)
        hook.argparser = argparser
        method = getattr(hook, evt)
        if method:
            try:
                method(*args, **kwargs)
            except Exception as _:
                debug_traceback(sys.exc_info(), __file__)


class ThreadGroup(object):
    """
    Thread group wrapper
    """
    def __init__(self, daemon=True, timeout=1.0, restart=True):
        self.daemon = daemon
        self.restart = restart
        self.threads = []
        self._targets = []
        self.timeout = timeout

    @property
    def targets(self):
        """
        Managed attribute, return list of thread targets
        """
        return self._targets

    @targets.setter
    def targets(self, th):
        """
        Managed attribute, set list of thread targets
        """
        self._targets = th

    def start_all(self):
        """
        Start all thread targets using restart_on_crash helper
        """
        for target in self._targets:
            if isinstance(target, list):
                # FIXME: Check for string args as well
                # works for subprocess.call only so far
                args = target[1:][0]
                target = target[0]
            else:
                args = ()
            name = repr(target)
            if self.restart:
                args = (target, args) if args else (target,)
                target = restart_on_crash
            # attempt to normalize args format
            elif args:
                args = (args,)
            thread = threading.Thread(name=name, target=target, args=args)
            thread.daemon = self.daemon
            thread.start()
            self.threads.append(thread)

    def stop_all(self):
        """
        Stop all thread targets
        """
        for thread in self.threads:
            thread.join(timeout=self.timeout)


def cmp(x, y):
    """
    CMP function introduced for compatibility
    TODO: get rid of this one
    """
    return (x > y) - (x < y)


def unbreakable_input():
    """
    Ignore keyboard interrupts and return value (used in configuration dialog)
    """
    while True:
        try:
            data = input()
        except KeyboardInterrupt:
            continue
        break
    return data


class SingleQueueDispatcher(object):
    """
    Bidirectional, single queue communication layer
    """
    TTL = 30
    def __init__(self, queue=None):
        self.queue = queue
        self.exit = False

    def set_exit(self):
        """
        Set exit flag
        """
        self.exit = True

    def send_and_wait(self, message):
        """
        Send message and wait for response
        """
        uuid = uuid4()
        full_msg = {'expires': int(time.time()) + self.TTL,
                    'uuid': uuid,
                    'message': message}
        self.queue.put(full_msg)
        exit_stamp = int(time.time()) + self.TTL
        while int(time.time()) <= exit_stamp and not self.exit:
            if not self.queue.empty():
                full_msg = self.queue.get()
                # purge expired messages
                if int(time.time()) >= int(full_msg.get('expires')):
                    logger.debug('Message %s - %s expired, purging...', int(time.time()), full_msg)
                    continue
                # get/check message
                if full_msg.get('uuid') != uuid:
                    logger.debug('Message %s not for me %s, requeueing...', full_msg, uuid)
                    self.queue.put(full_msg)
                else:
                    message = full_msg.get('message', '')
                    break
            time.sleep(0.01)
        return message

    def get_full_message(self):
        """
        Get message from queue
        """
        message = {}
        while not self.exit:
            if not self.queue.empty():
                message = self.queue.get()
                break
            time.sleep(0.01)
        logger.debug('SQD get: %r', message)
        return message

    def put_message(self, uuid, message):
        """
        Put message into queue
        """
        full_msg = {'expires': int(time.time()) + self.TTL,
                    'uuid': uuid,
                    'message': message}
        logger.debug('SQD put: %r', message)
        self.queue.put(full_msg)


class SignalHandler(object):
    """
    Signal handling class
    """
    def __init__(self):
        pass

    def register(self):
        """
        Register signal traps
        """
        logger.debug('%s: %s: %s', self.__class__.__name__, 'my pid is', os.getpid())
        signal.signal(signal.SIGHUP, self.receive_signal)
        signal.signal(signal.SIGUSR1, self.receive_signal)
        signal.signal(signal.SIGUSR2, self.receive_signal)

    def receive_signal(self, signum, stack):
        """
        A do-nothing signal trap
        """
        logger.debug('%s: %s: %s', self.__class__.__name__, 'Received:', signum)
