''' Configuration reader module '''
import kaptan

class Config(object):
    def __init__(self, cfg_file='config.yaml'):
        self.config = kaptan.Kaptan()
        self.config.import_config(cfg_file)

    @classmethod
    def cfg_data(cls):
        '''
        Return configuration data as dictionary
        '''
        obj = cls()
        return obj.config.configuration_data
