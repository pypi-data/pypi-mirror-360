import unittest
from unittest.mock import MagicMock, AsyncMock

from slidetextbridge.plugins.jmespath_filter import JMESPathFilter
from slidetextbridge.plugins import base

class DummySlide(base.SlideBase):
    def __init__(self, data=None):
        self._data = data or {}

    def to_dict(self):
        return self._data


class TestJMESPathFilter(unittest.IsolatedAsyncioTestCase):

    def test_type_name(self):
        self.assertEqual(JMESPathFilter.type_name(), 'jmespath')

    def test_config(self):
        cfg_filter = 'filter-text'
        cfg = JMESPathFilter.config(
                data = {'filter': cfg_filter}
        )

        self.assertEqual(cfg.filter, cfg_filter)

    async def test_update_filters_slide(self):
        ctx = MagicMock()

        cfg = MagicMock()
        cfg.src = 'dummy'
        cfg.filter = 'shapes[?val==`2`]'

        filter_obj = JMESPathFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()

        slide = DummySlide(data={'shapes': [{'name': 'a', 'val': 1}, {'name': 'b', 'val': 2}]})

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        emitted_slide = filter_obj.emit.await_args[0][0]
        self.assertIsInstance(emitted_slide, DummySlide)
        self.assertEqual(emitted_slide.to_dict(), [{'name': 'b', 'val': 2}])

if __name__ == '__main__':
    unittest.main()
