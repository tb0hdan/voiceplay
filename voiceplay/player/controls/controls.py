#-*- coding: utf-8 -*-
""" API player controls package """

from voiceplay.webapp.baseresource import APIV1Resource

class PlayerControlResource(APIV1Resource):
    route = '/api/v1/control/<command>'
    queue = None
    def post(self, command):
        # TODO: Add previous and volume
        safe_api_commands = ['pause', 'next', 'stop', 'resume']
        if self.queue and command and command in safe_api_commands:
            self.queue.put(command)
        return {'status': 'ok'}
