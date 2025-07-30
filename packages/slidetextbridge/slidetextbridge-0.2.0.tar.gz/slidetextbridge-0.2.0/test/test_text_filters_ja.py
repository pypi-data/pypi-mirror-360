import unittest
from unittest.mock import MagicMock, AsyncMock

from slidetextbridge.plugins import text_filters

from test.filter_helper import *

class TestTextFiltersJa(unittest.IsolatedAsyncioTestCase):

    async def test_linebreak_filter_split(self):
        ctx = MagicMock()

        # Check the punctuation will overflow.
        cfg = text_filters.TextLinebreakFilter.config({
            'split_long_line': 52,
            'split_nowrap': '、。」』,.',
            'split_nowrap_allow_overflow': True,
        })
        filter_obj = text_filters.TextLinebreakFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()
        slide = make_slide([
            'そのとき、イエスは言われた、「父よ、彼らをおゆるしください。彼らは何をしているのか、わからずにいるのです」。'
            + '人々はイエスの着物をくじ引きで分け合った。\n'
            + '民衆は立って見ていた。',
            '。' * 28,
            ])

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['\n'.join((
            'そのとき、イエスは言われた、「父よ、彼らをおゆるしく',
            'ださい。彼らは何をしているのか、わからずにいるのです」。',
            '人々はイエスの着物をくじ引きで分け合った。',
            '民衆は立って見ていた。'
            )), '。' * 28])

        # Check the punctuation won't overflow by wrapping at previous char.
        filter_obj.cfg.split_nowrap_allow_overflow = False
        filter_obj.emit = AsyncMock()

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['\n'.join((
            'そのとき、イエスは言われた、「父よ、彼らをおゆるしく',
            'ださい。彼らは何をしているのか、わからずにいるので',
            'す」。人々はイエスの着物をくじ引きで分け合った。',
            '民衆は立って見ていた。'
            )), '。' * 28])

        # Check if there is a space.
        slide = make_slide([
            '34 そのとき、イエスは言われた、「父よ、彼らをおゆるしください。彼らは何をしているのか、わからずにいるのです」。'
            + '人々はイエスの着物をくじ引きで分け合った。'
            ])
        filter_obj.cfg.split_nowrap_allow_overflow = True
        filter_obj.emit = AsyncMock()

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['\n'.join((
            '34 そのとき、イエスは言われた、「父よ、彼らをおゆる',
            'しください。彼らは何をしているのか、わからずにいるの',
            'です」。人々はイエスの着物をくじ引きで分け合った。',
            ))])

        # Check if there are non-CJK words and spaces in Japanese text.
        slide = make_slide([''.join((
            'Χριστοῦ Ἰησοῦ の僕、神の福音のために選び別たれ、召されて使徒となった Παῦλος から ',
            '―― この福音は、神が、預言者たちにより、聖書の中で、あらかじめ約束されたもので',
            'あって、 御子に関するものである。御子は、肉によれば Δαυὶδ の子孫から生れ、聖',
            'なる霊によれば、死人からの復活により、御力をもって神の御子と定められた。これがわ',
            'たしたちの主 Ἰησοῦ Χριστοῦ である。'
            )) ])
        filter_obj.emit = AsyncMock()
        filter_obj.cfg.split_long_line = 48

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['\n'.join((
            'Χριστοῦ Ἰησοῦ の僕、神の福音のために選び別たれ、',
            '召されて使徒となった Παῦλος から ―― この福音は、',
            '神が、預言者たちにより、聖書の中で、あらかじめ約',
            '束されたものであって、 御子に関するものである。',
            '御子は、肉によれば Δαυὶδ の子孫から生れ、聖なる',
            '霊によれば、死人からの復活により、御力をもって神',
            'の御子と定められた。これがわたしたちの主 Ἰησοῦ', # <-- Hit the case the non-CJK word is at the end.
            'Χριστοῦ である。'
            ))])


if __name__ == '__main__':
    unittest.main()
