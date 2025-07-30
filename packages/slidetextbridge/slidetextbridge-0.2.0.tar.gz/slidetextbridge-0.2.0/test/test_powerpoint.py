import sys
import types
import unittest
from unittest.mock import MagicMock, patch

mock_win32com_client = types.SimpleNamespace(Dispatch=lambda x: None)
mock_win32com = types.SimpleNamespace(client=mock_win32com_client)
mock_pywintypes = types.SimpleNamespace(com_error=Exception)
sys.modules['win32com'] = mock_win32com
sys.modules['win32com.client'] = mock_win32com_client
sys.modules['pywintypes'] = mock_pywintypes

from slidetextbridge.plugins import powerpoint # pylint: disable=C0413

def mock_shape(text, shape_type=14, name='unnamed'):
    shape = MagicMock()

    shape.HasTextFrame = True
    shape.TextFrame = MagicMock()
    shape.TextFrame.TextRange = MagicMock()
    shape.TextFrame.TextRange.Text = text
    shape.TextFrame.TextRange.HasText = len(text) > 0
    shape.TextFrame.TextRange.Count = len(text)
    shape.TextFrame.TextRange.Start = 0
    shape.TextFrame.TextRange.Length = len(text)
    shape.TextFrame.TextRange.BoundLeft = 0
    shape.TextFrame.TextRange.BoundTop = 0
    shape.TextFrame.TextRange.BoundWidth = 1
    shape.TextFrame.TextRange.BoundHeight = 1
    shape.TextFrame.TextRange.Font = MagicMock()
    shape.TextFrame.TextRange.Font.Size = 24
    shape.TextFrame.TextRange.Font.Bold = False
    shape.TextFrame.TextRange.Font.Name = name
    shape.TextFrame.TextRange.Font.BaselineOffset = 0
    shape.TextFrame.TextRange.Font.Italic = False
    shape.TextFrame.TextRange.Font.Subscript = False
    shape.TextFrame.TextRange.Font.Superscript = False
    shape.TextFrame.HasText = True
    shape.TextFrame.Orientation = 0
    shape.TextFrame.WordWrap = False

    shape.PlaceholderFormat = MagicMock()
    shape.PlaceholderFormat.Name = name
    shape.PlaceholderFormat.Type = 1
    shape.PlaceholderFormat.ContainedType = 2

    shape.Type = shape_type
    shape.Name = name

    return shape

class TestPowerPointCapture(unittest.TestCase):
    def test_type_name(self):
        self.assertEqual(powerpoint.PowerPointCapture.type_name(), 'ppt')

    @patch('win32com.client.Dispatch', autospec=True)
    def test_update(self, MockDispatch):
        ctx = MagicMock()

        ppt = MagicMock()
        MockDispatch.return_value = ppt

        cfg = powerpoint.PowerPointCapture.config({})
        obj = powerpoint.PowerPointCapture(ctx=ctx, cfg=cfg)

        win = MagicMock()
        api_slide = MagicMock()
        ppt.SlideShowWindows.Count.return_value = 1
        ppt.SlideShowWindows.return_value = win
        win.View = MagicMock()
        win.View.State = 0
        win.View.Slide = api_slide

        api_slide.Shapes = [
                mock_shape(text='a'),
        ]

        int_slide = obj._get_slide()
        slide = powerpoint.PowerPointSlide(int_slide, cfg=obj.cfg)

        self.assertEqual(int_slide, api_slide)
        self.assertEqual(str(slide), 'a')
        # self.maxDiff = None
        d = slide.to_dict()
        self.assertEqual(d['shapes'][0]['text_frame']['has_text'], True)
        self.assertEqual(d['shapes'][0]['text_frame']['text_range']['text'], 'a')
        # TODO: Check other fields. I should copy the expected data from actual PowerPoint.



if __name__ == "__main__":
    unittest.main()
