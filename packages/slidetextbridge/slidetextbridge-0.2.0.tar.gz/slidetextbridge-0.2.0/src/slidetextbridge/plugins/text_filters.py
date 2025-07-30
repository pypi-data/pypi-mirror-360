'''
Filters to modify texts
'''

import re
import logging
from slidetextbridge.core import config
from . import base


_CJK_RANGES = (
          (0x03300, 0x033FF),  # compatibility ideographs
          (0x0FE30, 0x0FE4F),  # compatibility ideographs
          (0x0F900, 0x0FAFF),  # compatibility ideographs
          (0x2F800, 0x2FA1F),  # compatibility ideographs
          (0x03000, 0x0303F),  # CJK symbols and punctuation
          (0x03040, 0x030FF),  # Japanese Hiragana and Katakana
          (0x03190, 0x0319F),  # Kanbun
          (0x02E80, 0x02EFF),  # CJK radicals supplement
          (0x04E00, 0x09FFF),
          (0x03400, 0x04DBF),
          (0x0AC00, 0x0D7AF),  # Hangul Syllables
          (0x1B130, 0x1B16F),  # Small Kana Extension
          (0x20000, 0x2A6DF),
          (0x2A700, 0x2B73F),
          (0x2B740, 0x2B81F),
          (0x2B820, 0x2CEAF),  # included as of Unicode 8.0
)

def _is_cjk_char(c):
    c = ord(c)
    for r in _CJK_RANGES:
        if r[0] <= c <= r[1]:
            return True
    return False

class TextLinebreakFilter(base.PluginBase):
    '''
    Filter line breaks in texts
    '''

    @classmethod
    def type_name(cls):
        return 'linebreak'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('shape_delimiter', type=str, default='\n')
        cfg.add_argment('line_delimiter', type=str, default='\n')
        cfg.add_argment('strip', type=bool, default=True)
        cfg.add_argment('split_long_line', type=int, default=0)
        cfg.add_argment('split_nowrap', type=str, default='.,"\'')
        cfg.add_argment('split_nowrap_allow_overflow', type=bool, default=True)
        cfg.add_argment('joined_column_max', type=int, default=0)
        cfg.add_argment('join_by', type=str, default=' ')
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'linebreak({self.cfg.location})')
        self.connect_to(cfg.src)

    def _filter_shape_text(self, text):
        lines = text.split('\n')

        if self.cfg.strip:
            stripped = []
            for t in lines:
                t = t.strip()
                if t:
                    stripped.append(t)
            lines = stripped

        if self.cfg.split_long_line:
            new_lines = []
            for line in lines:
                new_lines += self._split_long_line(line)
            lines = new_lines

        if self.cfg.joined_column_max:
            joined = []
            pending_text = None
            for t in lines:
                next_text = pending_text + self.cfg.join_by + t if pending_text else t
                nt = self._count_text(next_text)
                if nt > self.cfg.joined_column_max:
                    if pending_text:
                        joined.append(pending_text)
                    pending_text = t
                else:
                    pending_text = next_text
            if pending_text:
                joined.append(pending_text)
            lines = joined

        return self.cfg.line_delimiter.join(lines)

    def _split_long_line(self, text):
        # pylint: disable=R0912
        if self._count_text(text) <= self.cfg.split_long_line:
            yield text
            return

        while text:
            # Find the length that satisfies `split_long_line`
            ix = 0
            ix_cjk = -1
            ix_space = -1
            ix_other = -1
            n = 0
            allow_overflow = False
            while ix < len(text):
                c = text[ix]
                n += self._count_text(c)
                allow_overflow = False
                if c.isspace():
                    ix_space = ix
                elif self.cfg.split_nowrap and c in self.cfg.split_nowrap:
                    if self.cfg.split_nowrap_allow_overflow:
                        allow_overflow = True
                elif _is_cjk_char(c):
                    ix_cjk = ix
                else:
                    ix_other = ix

                if not allow_overflow and n > self.cfg.split_long_line:
                    break
                ix += 1

            if ix == len(text):
                yield text
                break

            # If there is a space, let's cut at the space.
            if ix_space > 0 and ix_space > ix_cjk:
                yield text[:ix_space]
                text = text[ix_space+1:]

            # If there is a CJK string,
            elif ix_cjk > 0:
                yield text[:ix_cjk]
                text = text[ix_cjk:]

            # If no more option to break
            elif ix_other > 0:
                yield text[:ix_other]
                text = text[ix_other:]

            # The last condition to avoid infinite loop
            # Will reach when satisfying both of these conditions.
            # - There are only nowrap characters but exceeding the threshold.
            # - allow_overflow = false.
            else:
                yield text
                break

    def _count_text(self, text):
        'Count CJK characters twice'
        if text.isascii():
            return len(text)
        n = 0
        for c in text:
            n += 2 if _is_cjk_char(c) else 1
        return n

    async def update(self, slide, args):
        texts = slide.to_texts()
        shapes = [{
            'text': self._filter_shape_text(t),
            'shape_delimiter': self.cfg.shape_delimiter
            } for t in texts]
        slide = TextFilteredSlide(data={'shapes': shapes}, parent=self)
        await self.emit(slide)


def _parse_patterns(v):
    cfg = config.ConfigBase()
    cfg.add_argment('p', type=str)
    cfg.add_argment('r', type=str)
    ret = []
    for pattern in v:
        cfg.parse(pattern)
        ret.append((re.compile(cfg.p), cfg.r)) # pylint: disable=E1101

    return ret

class RegexFilter(base.PluginBase):
    '''
    Filter lines with regex
    '''

    @classmethod
    def type_name(cls):
        return 'regex'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('patterns', conversion=_parse_patterns)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'regex({self.cfg.location})')
        self.connect_to(cfg.src)

    def _filter_shape_text(self, text):
        lines = text.split('\n')
        for p, r in self.cfg.patterns:
            lines = [p.sub(r, t) for t in lines]
        return '\n'.join(lines)

    async def update(self, slide, args):
        if isinstance(slide, TextFilteredSlide):
            d = slide.to_dict()
            for shape in d['shapes']:
                shape['text'] = self._filter_shape_text(shape['text'])
        else:
            texts = slide.to_texts()
            shapes = [{
                'text': self._filter_shape_text(t),
                } for t in texts]
            slide = TextFilteredSlide(data={'shapes': shapes}, parent=self)
        await self.emit(slide)


class TextFilteredSlide(base.SlideBase):
    'The slide class returned by the filters'

    def __init__(self, data=None, parent=None):
        if isinstance(data, list):
            self._dict = {'shapes': data}
        else:
            self._dict = data
        self.parent = parent

    def to_texts(self):
        try:
            if self._dict:
                return [shape['text'] for shape in self._dict['shapes']]
        except (TypeError, KeyError) as e:
            logger = self.parent.logger if self.parent else logging.getLogger('TextFilteredSlide')
            logger.error('Failed to convert slide to texts. %s', e)
        return []

    def __str__(self):
        ret = ''
        shape_delimiter = ''
        for shape in self._dict['shapes']:
            ret += shape_delimiter
            ret += shape['text']
            shape_delimiter = shape['shape_delimiter'] if 'shape_delimiter' in shape else '\n'
        return ret

    def to_dict(self):
        return self._dict
