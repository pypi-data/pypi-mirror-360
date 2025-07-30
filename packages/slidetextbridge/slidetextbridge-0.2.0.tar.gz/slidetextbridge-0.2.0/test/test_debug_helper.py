import json
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from slidetextbridge.plugins import debug_helper

from test.filter_helper import *

class TestStdoutEmitter(unittest.IsolatedAsyncioTestCase):

    def test_type_name(self):
        self.assertEqual(debug_helper.StdoutEmitter.type_name(), 'stdout')

    async def test_stdout(self):

        with patch('sys.stdout.write') as mock_write:
            res = await run_filter(
                    debug_helper.StdoutEmitter,
                    {},
                    make_slide(['A', 'B'])
            )
            text = ''.join(x[0][0] for x in mock_write.call_args_list)
        self.assertEqual(text, 'A\nB\n\n')

        with patch('sys.stdout.write') as mock_write:
            res = await run_filter(
                    debug_helper.StdoutEmitter,
                    {'page_delimiter': 'C'},
                    make_slide(['A', 'B'])
            )
            text = ''.join(x[0][0] for x in mock_write.call_args_list)
        self.assertEqual(text, 'A\nBC')

    async def test_stdout_json(self):
        slide = make_slide(['A', 'B'])
        with patch('sys.stdout.write') as mock_write:
            res = await run_filter(
                    debug_helper.StdoutEmitter,
                    {'json': True},
                    slide
            )
            text = ''.join(x[0][0] for x in mock_write.call_args_list)
        self.assertEqual(json.loads(text), slide.to_dict())
