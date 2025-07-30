'''
Base class definition
'''

import logging
import re

def set_config_arguments(cfg, has_src=True):
    '''
    Set the standard config arguments
    :param cfg:  Instance of ConfigBase
    '''
    cfg.add_argment('type', type=str)
    cfg.add_argment('name', type=str, default=None)
    if has_src:
        cfg.add_argment('src', type=str, default=None)


class PluginBase:
    '''
    The base class for text sources, filters, and sinks.
    '''

    @classmethod
    def type_name(cls):
        'Return the name of the type'
        return 'base'

    def __init__(self, ctx, cfg=None):
        self.ctx = ctx
        self.cfg = cfg
        self.name = cfg.name
        self.sinks = []
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(f'{__name__}({self.cfg.location})')

    def connect_to(self, name=None, args=None):
        '''
        Connect this instance to the source of the text.
        :param name:  The name of the source
        :param args:  The argument that will be passed to `update` callback
        '''
        src = self.ctx.get_instance(name=name)
        return src.add_sink(self, args=args)

    def add_sink(self, sink, args=None):
        '''
        Connect a sink, that will receive the contents of this plugin.
        :param sink:  The instance of PluginBase
        :param args:  Any object
        '''
        self.sinks.append((sink, args))

    async def initialize(self):
        '''
        Callback when the system is started.
        '''

    async def emit(self, slide):
        '''
        Send the new slide to all sinks.
        :param slide:  The new slide.
        '''
        for sink, args in self.sinks:
            try:
                await sink.update(slide, args)
            except Exception as e:
                self.logger.error('Failed to send text to %s. %s', type(sink), e)

    async def update(self, slide, args):
        '''
        The callback function when updating the new slide.
        '''


class SlideBase():
    '''
    The base class representing the current slide
    '''
    def __init__(self, slide=None, data=None):
        pass

    def to_texts(self):
        '''
        List all texts
        :return:  List of strings
        '''
        return []

    def __str__(self):
        return '\n'.join(self.to_texts())

    @staticmethod
    def convert_object(obj, params=()):
        '''
        A helper method to convert an object to dict type.
        :param params:  List of attributes that will be converted to the dict item.
        Each element of `params` can be a string or a 2-element tuple.
        '''
        d = {}
        def _f(attrname, f_conv=None):
            dest = re.sub('(.)([A-Z])', r'\1_\2', attrname).lower()
            try:
                v = getattr(obj, attrname)
            except: # pylint: disable=W0702
                return
            if f_conv:
                v = f_conv(v)
            d[dest] = v
        for p in params:
            if isinstance(p, tuple):
                _f(p[0], p[1])
            else:
                _f(p)
        return d

    def to_dict(self):
        '''
        Get the dict object so that jmespath can filter it.
        The jmespath filter will then calls the initializer of the class
        with a `data` parameter to create a new slide object.
        :return: dict object representing this object
        '''
        return {}
