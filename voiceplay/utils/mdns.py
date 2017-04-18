#-*- coding: utf-8 -*-
""" ZeroConf service registration """

import socket
import time
import uuid

from zeroconf import (ServiceBrowser,
                      ServiceInfo,
                      ServiceStateChange,
                      Zeroconf)

from voiceplay.config import Config
from voiceplay.utils.helpers import ThreadGroup
from voiceplay import __title__


class VoicePlayZeroConf(object):
    """
    Very basic mDNS/Zeroconf check/registration
    """
    def __init__(self):
        self.zeroconf = None
        self.known_servers = []
        self.info = None
        self.threads = None
        self.exit = False

    @staticmethod
    def get_ip_address():
        """
        Get my IP
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    def service_info(self, hostname):
        """
        Prepare service information for (my) hostname
        """
        port = int(Config.cfg_data().get('webapp_port'))
        info = ServiceInfo("_http._tcp.local.",
                           "{0!s}._http._tcp.local.".format(hostname),
                           socket.inet_aton(self.get_ip_address()), port, 0, 0,
                           {'path': '/'}, "{0!s}.local.".format(hostname))
        return info

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        """
        Service state change callback
        """
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and not info.server in self.known_servers:
                self.known_servers.append(info.server)

    def get_others(self):
        """
        Wait for other services to make themselves visible
        """
        zeroconf = Zeroconf()
        _ = ServiceBrowser(zeroconf, "_http._tcp.local.", handlers=[self.on_service_state_change])
        for _ in range(1, 10 + 1):
            time.sleep(1)
        zeroconf.close()
        return self.known_servers

    def run(self):
        """
        Actual Zeroconf runner
        """
        # has to be here, otherwise quick start/stop will not provide self.zeroconf descriptor
        self.zeroconf = Zeroconf()
        servers = self.get_others()
        hostname = __title__.lower()
        if '{0!s}.local'.format(hostname) in servers:
            hostname = '{0!s}-{1!s}'.format(__title__.lower(), str(uuid.uuid4()))
        self.info = self.service_info(hostname)
        self.zeroconf.register_service(self.info)
        while not self.exit:
            try:
                time.sleep(0.1)
            except Exception as _:
                break

    def unregister(self):
        """
        Unregister (remove) service from local network
        """
        if self.info:
            self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

    def start(self):
        """
        Start Zeroconf inside thread
        """
        self.threads = ThreadGroup()
        self.threads.targets = [self.run]
        self.threads.start_all()

    def stop(self):
        """
        Stop and unregister Zeroconf service
        """
        self.exit = True
        self.unregister()
        if self.threads:
            self.threads.stop_all()
