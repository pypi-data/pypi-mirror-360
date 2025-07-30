'''
Get text from Microsoft PowerPoint
'''

import asyncio
import logging
import win32com.client
import pywintypes
from slidetextbridge.core import config
from slidetextbridge.core.logging import HideSameLogFilter
from . import base


class _Const:
    # pylint: disable=R0903
    ppSlideShowBlackScreen = 3
    ppSlideShowWhiteScreen = 4
    ppSlideShowDone = 5


class PowerPointCapture(base.PluginBase):
    '''
    Get text from Microsoft PowerPoint
    '''
    @classmethod
    def type_name(cls):
        return 'ppt'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg, has_src=False)
        cfg.add_argment('placeholder_only', type=bool, default=True)
        cfg.add_argment('poll_wait_time', type=float, default=0.1)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'ppt({self.cfg.location})')
        self.logger.addFilter(HideSameLogFilter())
        self._last_slide = self
        self.ppt = None
        self._last_window = None

    async def initialize(self):
        asyncio.create_task(self._loop())

    async def _loop(self):
        while True:
            try:
                slide = self._get_slide()
                if slide != self._last_slide:
                    self._last_slide = slide
                    await self.emit(PowerPointSlide(slide, cfg=self.cfg))

                await asyncio.sleep(self.cfg.poll_wait_time)
            except Exception as e:
                self.logger.error('Unknown error: %s', e)
                await asyncio.sleep(1)

    def _connect_ppt(self):
        self.logger.info('Connecting to PowerPoint...')
        self.ppt = win32com.client.Dispatch("PowerPoint.Application")
        self._last_window = None
        if self.ppt:
            self.logger.info('Connected to PowerPoint.')
        else:
            self.logger.warning('Failed to connect to PowerPoint.')

    def _current_slideshow_window(self):
        if not self.ppt:
            self._connect_ppt()
            if not self.ppt:
                return None
        try:
            slide_count = self.ppt.SlideShowWindows.Count
        except (pywintypes.com_error, AttributeError): # pylint: disable=no-member
            self.ppt = None
            self._last_window = None
            return None

        if slide_count == 0:
            self.logger.warning('No current presentation window.')
            return None

        if slide_count == 1:
            self._last_window = self.ppt.SlideShowWindows(1)
            return self._last_window

        cand = None
        for ix in range(slide_count):
            w = self.ppt.SlideShowWindows(ix + 1)
            if w.Active:
                self._last_window = w
                return w
            if w == self._last_window:
                cand = w
        return cand

    def _get_slide(self):
        w = self._current_slideshow_window()
        if not w:
            # no current presentation window
            return None

        view = w.View

        if view.State in (
                _Const.ppSlideShowBlackScreen,
                _Const.ppSlideShowWhiteScreen,
                _Const.ppSlideShowDone):
            return None

        return view.Slide


def _com32bool_to_bool(b):
    return bool(b)

def _font_to_dict(font):
    return base.SlideBase.convert_object(font, params=(
        'Size', 'Bold', 'Name', 'BaselineOffset',
        ('Italic', _com32bool_to_bool),
        ('Subscript', _com32bool_to_bool),
        ('Superscript', _com32bool_to_bool),
    ))

def _tr_to_dict(tr):
    return base.SlideBase.convert_object(
            tr,
            params=(
                ('HasText', _com32bool_to_bool),
                'Text',
                'Count', 'Start', 'Length',
                'BoundLeft', 'BoundTop', 'BoundWidth', 'BoundHeight',
                ('Font', _font_to_dict),
            ),
    )

def _tf_to_dict(tf):
    return base.SlideBase.convert_object(tf, params=(
        ('HasText', _com32bool_to_bool),
        ('TextRange', _tr_to_dict),
        'Orientation',
        ('WordWrap', _com32bool_to_bool),
    ))

def _pf_to_dict(pf):
    return base.SlideBase.convert_object(pf, params=('Name', 'Type', 'ContainedType'))

class PowerPointSlide(base.SlideBase):
    'The slide class returned by PowerPointCapture'

    def __init__(self, slide=None, data=None, cfg=None):
        self._slide = slide
        self.cfg = cfg
        if isinstance(data, list):
            self._dict = {'shapes': data}
        else:
            self._dict = data

    def _shape_is_valid(self, shape):
        if not shape.HasTextFrame or not shape.TextFrame.HasText:
            return False
        if self.cfg and self.cfg.placeholder_only:
            if shape.Type != 14:
                return False
        return True

    def to_texts(self):
        '''
        List all texts
        :return:  List of strings
        '''
        if self._dict:
            return _list_texts(self._dict)

        if not self._slide:
            return []

        texts = []
        for shape in self._slide.Shapes:
            if not self._shape_is_valid(shape):
                continue
            texts.append(shape.TextFrame.TextRange.Text.replace('\r', ' '))
        return texts

    def to_dict(self):
        if self._dict:
            return self._dict
        if not self._slide:
            return {}
        shapes = []
        for shape in self._slide.Shapes:
            if not self._shape_is_valid(shape):
                continue
            s = base.SlideBase.convert_object(shape, params=(
                ('TextFrame', _tf_to_dict),
                'Type',
                ('PlaceholderFormat', _pf_to_dict),
                'Name',
            ))
            shapes.append(s)
        self._dict = {'shapes': shapes}
        return self._dict


def _list_texts(obj):
    if isinstance(obj, str):
        return [obj, ]
    if isinstance(obj, (int, float, bool)):
        return []
    if isinstance(obj, dict):
        for key in ('shapes', 'text', 'text_range', 'text_frame'):
            if key in obj:
                return _list_texts(obj[key])
        return []
    ret = []
    for x in obj:
        if x:
            ret += _list_texts(x)
    return ret
