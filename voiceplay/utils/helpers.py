#-*- coding: utf-8 -*-
''' Helper functions / methods / classes '''


class Singleton(type):
    '''
    Singleton base class
    '''
    cls_instances = {}
    def __call__(cls, *args, **kwargs):
        '''
        Handle instantiation
        '''
        if cls not in cls.cls_instances:
            cls.cls_instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.cls_instances[cls]
