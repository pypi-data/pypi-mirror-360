'''
Helper classes for debugging
'''

import json
import logging
import sys
from slidetextbridge.core import config
from . import base


class StdoutEmitter(base.PluginBase):
    '''
    Just print to stdout
    '''
    @classmethod
    def type_name(cls):
        return 'stdout'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('page_delimiter', type=str, default='\n\n')
        cfg.add_argment('json', type=bool, default=False)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'stdout({self.cfg.location})')
        self.connect_to(cfg.src)

    async def update(self, slide, args):
        try:
            if self.cfg.json:
                text = json.dumps(slide.to_dict(), ensure_ascii=False, indent=2)
            elif not slide:
                text = ''
            else:
                text = str(slide)

            sys.stdout.write(f'{text}{self.cfg.page_delimiter}')
        except Exception as e:
            self.logger.error('%s', e)

        await self.emit(slide)
