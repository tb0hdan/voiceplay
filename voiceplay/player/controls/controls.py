#-*- coding: utf-8 -*-
""" API player controls package """

from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher


class PlayerControlResource(APIV1Resource):
    route = '/api/v1/control/<command>'
    queue = None
    def post(self, command):
        result = {'status': 'timeout', 'message': ''}
        # TODO: Add previous and volume
        safe_api_commands = ['pause', 'next', 'stop', 'resume']
        if self.queue and command and command in safe_api_commands:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait(command)
            result = {'status': 'ok', 'message': message}
        return result
