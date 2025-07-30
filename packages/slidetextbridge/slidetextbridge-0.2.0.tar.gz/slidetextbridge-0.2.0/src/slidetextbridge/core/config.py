'''
Configuration data structure
'''

_LIB_KEYS = ('_location', )

class ConfigBase():
    '''
    Base class to hold configuration data
    '''
    def __init__(self):
        self.argtypes = []
        self.location = None

    def add_argment(self, *args, **kwargs):
        '''
        Add an argument for this configuration type.
        Call this method before `parse`.
        :param name:       name of the argument (`snake_case` is recommended)
        :param type:       type of the argument
        :param conversion: conversion function taking one argument
        :param default:    the default value
        '''
        class _Argment:
            # pylint: disable=W0622,R0903
            def __init__(self, name, type=None, conversion=None, default=None):
                self.name = name
                self.type = type
                self.conversion = conversion
                self.default = default
        self.argtypes.append(_Argment(*args, **kwargs))

    def parse(self, d: dict):
        '''
        Parse the dictionary data and set attributes
        :param d:  data
        '''
        self.location = d['_location'] if '_location' in d else None
        for key in d.keys():
            if key in _LIB_KEYS:
                continue
            found = False
            for a in self.argtypes:
                if a.name == key:
                    found = True
                    break
            if not found:
                raise KeyError(f'{self.location}: {key} is undefined')
        for a in self.argtypes:
            if a.name in d:
                v = d[a.name]
                if a.conversion:
                    v = a.conversion(v)
                elif a.type:
                    v = a.type(v)
            else:
                v = a.default
            setattr(self, a.name, v)
