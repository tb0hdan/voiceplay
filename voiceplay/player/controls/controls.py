#-*- coding: utf-8 -*-
""" API player controls package """

from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from voiceplay.utils.command import Command

class PlayerControlResource(APIV1Resource):
    """
    Player control API endpoint
    """
    route_base = '/api/v1/control/<command>'
    queue = None
    def post(self, command):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        # TODO: Add previous and volume
        safe_api_commands = [Command.PAUSE, Command.NEXT, Command.STOP, Command.RESUME]
        if self.queue and command and command in safe_api_commands:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait(command)
            result = {'status': 'ok', 'message': message}
        return result
