import unittest
from unittest.mock import MagicMock, AsyncMock

from slidetextbridge.core import context

class TestContext(unittest.IsolatedAsyncioTestCase):

    def test_instances(self):

        ctx = context.Context()

        inst1 = MagicMock()
        inst1.name = 'name1'
        inst2 = MagicMock()
        inst2.name = 'name2'

        ctx.add_instance(inst1)

        self.assertEqual(ctx.get_instance(), inst1)

        ctx.add_instance(inst2)

        self.assertEqual(ctx.get_instance('name1'), inst1)
        self.assertEqual(ctx.get_instance('name2'), inst2)
        self.assertEqual(ctx.get_instance(), inst2)

    async def test_init(self):

        ctx = context.Context()

        inst1 = AsyncMock()
        inst2 = AsyncMock()

        ctx.add_instance(inst1)
        ctx.add_instance(inst2)

        await ctx.initialize_all()

        inst1.initialize.assert_awaited_once()
        inst2.initialize.assert_awaited_once()

if __name__ == '__main__':
    unittest.main()
