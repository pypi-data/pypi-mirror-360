import unittest
from unittest.mock import MagicMock, AsyncMock

from slidetextbridge.plugins import text_filters

from test.filter_helper import *


class TestTextFilters(unittest.IsolatedAsyncioTestCase):

    def test_type_name(self):
        self.assertEqual(text_filters.TextLinebreakFilter.type_name(), 'linebreak')
        self.assertEqual(text_filters.RegexFilter.type_name(), 'regex')

    def test_config(self):
        cfg = text_filters.RegexFilter.config(
                data = {'patterns': [
                    {'p': 'p1', 'r': 'r1'},
                    {'p': 'p2', 'r': 'r2'},
                ]}
        )

        self.assertEqual(len(cfg.patterns), 2)
        self.assertEqual(cfg.patterns[0][0].pattern, 'p1')
        self.assertEqual(cfg.patterns[0][1], 'r1')
        self.assertEqual(cfg.patterns[1][0].pattern, 'p2')
        self.assertEqual(cfg.patterns[1][1], 'r2')

    async def test_linebreak_filter_strip(self):

        res = await run_filter(
                text_filters.TextLinebreakFilter,
                {'strip': True,},
                make_slide(['A', 'B ', ' C ', ' D'])
        )
        self.assertEqual(res.to_texts(), ['A', 'B', 'C', 'D'])

        res = await run_filter(
                text_filters.TextLinebreakFilter,
                {'strip': False,},
                make_slide(['A', 'B ', ' C ', ' D'])
        )
        self.assertEqual(res.to_texts(), ['A', 'B ', ' C ', ' D'])

    async def test_linebreak_filter_split_join(self):

        # Let's make a method that takes cfg, input_texts, and output_texts as the parameters.
        res = await run_filter(
                text_filters.TextLinebreakFilter,
                {
                    'split_long_line': 8,
                    'joined_column_max': 4,
                    'join_by': '-'
                },
                make_slide([
                    'abcdefghijk', # Check too long ASCII word
                    'a\nb',
                    '.'*12,
                ])
        )
        self.assertEqual(res.to_texts(), [
            'abcdefgh\nijk',
            'a-b',
            '.'*12,
        ])

        res = await run_filter(
                text_filters.TextLinebreakFilter,
                {
                    'split_long_line': 4,
                    'split_nowrap_allow_overflow': False,
                },
                make_slide([
                    'abc',
                    'abcd',
                    'abcde',
                    'abcdef',
                    '...',
                    '....',
                    '.....',
                    '......',
                ])
        )
        self.assertEqual(res.to_texts(), [
            'abc',
            'abcd',
            'abcd\ne',
            'abcd\nef',
            '...',
            '....',
            '.....',
            '......',
        ])

    async def test_linebreak_filter_delimiters(self):

        res = await run_filter(
                text_filters.TextLinebreakFilter,
                {
                    'shape_delimiter': '/',
                    'line_delimiter': ':',
                },
                make_slide([
                    'a\nb',
                    'c',
                ])
        )
        self.assertEqual(res.to_texts(), [
            'a:b',
            'c',
        ])
        self.assertEqual(str(res), 'a:b/c')

    async def test_regex_filter(self):

        res = await run_filter(
                text_filters.RegexFilter,
                {
                    'patterns': [
                        {'p': r'(Th|th)is', 'r': r'\1at'},
                    ],
                },
                slides=[
                    make_slide(['This is a pen.']),
                    make_slide(['Who is this?']),
                ],
        )
        self.assertEqual(res[0].to_texts(), ['That is a pen.'])
        self.assertEqual(res[1].to_texts(), ['Who is that?'])

    # TODO: Also check the combination with jmespath filter


if __name__ == '__main__':
    unittest.main()
