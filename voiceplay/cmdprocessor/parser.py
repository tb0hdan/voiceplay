import re

class MyParser(object):
    '''
    Parse text commands
    '''
    known_actions = {'play': [{r'^play (.+) station$': 'station_artist'},
                              {r'^play some (?:music|tracks?|songs?) by (.+)$': 'shuffle_artist'},
                              {r'^play top (?:songs|tracks) by (.+)$': 'top_tracks_artist'},
                              {r'^play top (?:songs|tracks)(?:\sin\s(.+))?$': 'top_tracks_geo'},
                              {r'^play (.+)?my library$': 'shuffle_local_library'},
                              {r'^play (?:songs|tracks) from (.+) by (.+)$': 'artist_album'},
                              {r'^play (.+) bu?(?:t|y) (.+)$': 'single_track_artist'}],
                     'shuffle': [{r'^shuffle (.+)?my library$': 'shuffle_local_library'}],
                     'shutdown': [{'shutdown': 'shutdown_action'},
                                  {'shut down': 'shutdown_action'}],
                     'what': [{r'^what are top albums (?:by|for) (.+)$': 'top_albums_artist'},
                              {r'^what are top (?:songs|tracks) (?:by|for) (.+)$': 'top_tracks_artist'}]
                    }

    def parse(self, message):
        '''
        Parse incoming message
        '''
        start = False
        action_phrase = []
        for word in message.split(' '):
            if self.known_actions.get(word):
                start = True
            if start and word:
                action_phrase.append(word)
        response = ' '.join(action_phrase)
        return response

    def get_action_type(self, action_phrase):
        '''
        Get action type depending on incoming message
        '''
        action = action_phrase.split(' ')[0]
        if self.known_actions.get(action, None) is None:
            raise ValueError('Unknown action %r in phrase %r' % (action, action_phrase))
        action_type = None
        for regs in self.known_actions.get(action):
            reg = list(regs.keys())[0]
            if re.match(reg, action_phrase) is not None:
                action_type = regs[reg]
                break
        if action_phrase and action_phrase.startswith('play') and not action_type:
            reg = '^play (.+)$'
            action_type = 'track_number_artist'
        return action_type, reg, action_phrase
