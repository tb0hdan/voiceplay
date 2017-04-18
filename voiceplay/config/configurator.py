#-*- coding: utf-8 -*-
""" Configuration dialog module """

from __future__ import print_function

# std
import os

# from's
from copy import deepcopy

# 3rd
import colorama
import kaptan
import pylast

# local
from voiceplay.utils.helpers import unbreakable_input
from .config import Config


class ConfigDialog(object):
    """
    Configuration dialog utility
    """
    template = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'config.yaml.sample')

    def __init__(self):
        print (self.template)
        self.cfg_data = Config(cfg_file=self.template).cfg_data()

    def run(self, fname):
        """
        Run configuration dialog
        """
        fname = os.path.expanduser(fname)
        if os.path.exists(fname):
            print ('Refusing to overwrite existing config at {0!s}'.format(fname))
            print ('Please rename it if you would like to proceed with this utility')
            return
        new_config = deepcopy(self.cfg_data)
        for service in sorted(Config.external_services):
            msg = '{0}{1}{2}{3}'.format(colorama.Fore.CYAN,
                                        colorama.Style.BRIGHT,
                                        self.cfg_data[service]['account_url'],
                                        colorama.Style.RESET_ALL)
            print ('Running configuration for {0!s}:\nPlease go to following URL: {1!s} and register account, after completing this step please press Enter.'.format(self.cfg_data[service]['description'], msg))
            unbreakable_input()
            for key in self.cfg_data.get(service):
                if key in ['account_url', 'description']:
                    continue
                data = ''
                while not data:
                    msg = '{0}{1}{2}{3}'.format(colorama.Fore.GREEN,
                                                colorama.Style.BRIGHT,
                                                key,
                                                colorama.Style.RESET_ALL)
                    print ('Please paste {0!s} and press Enter (CTRL+C to repeat)'.format(msg))
                    data = unbreakable_input()
                if service == 'lastfm' and key == 'password':
                    data = pylast.md(data)
                new_config[service][key] = data
        export_data = self.export(new_config)
        dirname = os.path.dirname(fname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        print ('Saving configuration file...')
        with open(fname, 'w') as config_file:
            config_file.write(export_data)

    @staticmethod
    def export(cfg_data):
        """
        Export data from configuration dialog
        """
        config = kaptan.Kaptan()
        config.import_config(cfg_data)
        return config.export('yaml')
