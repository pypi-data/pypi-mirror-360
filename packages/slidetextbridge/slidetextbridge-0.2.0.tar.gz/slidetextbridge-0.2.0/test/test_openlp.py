import sys
import json
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from slidetextbridge.plugins import openlp # pylint: disable=C0413

def _mock_poll(results):
    mockWSConnect = AsyncMock()
    mockWSConnect.return_value = AsyncMock()
    mockWSConnect.return_value.recv = AsyncMock()
    mockWSConnect.return_value.recv.return_value = json.dumps(
            {'results': results}
    )
    return patch('websockets.connect', mockWSConnect)

def _make_mock_request(data):
    mockResponse = AsyncMock()
    mockResponse.text.return_value = json.dumps(data)

    request_ctx = MagicMock()
    request_ctx.__aenter__ = AsyncMock(return_value=mockResponse)
    request_ctx.__aexit__ = AsyncMock(return_value=None)

    return MagicMock(return_value=request_ctx)


class TestOpenLPCapture(unittest.IsolatedAsyncioTestCase):
    def test_type_name(self):
        self.assertEqual(openlp.OpenLPCapture.type_name(), 'openlp')

    async def test_text(self):
        ctx = MagicMock()

        cfg = openlp.OpenLPCapture.config({})
        obj = openlp.OpenLPCapture(ctx=ctx, cfg=cfg)

        poll_results = {
                'counter': 4, 'service': 0, 'slide': 0, 'item': 'd61e5b58-530d-11f0-9697-6045cba385ca', 'twelve': True, 'blank': False, 'theme': False, 'display': False, 'version': 3, 'isSecure': False, 'chordNotation': 'english'
        }

        data = {
            "title": "Song Title", "name": "songs", "type": 1, "theme": None, "footer": ["Song Title", "Written by: The Author"], "audit": ["Song Title", ["The Author"], "", ""], "notes": "", "data": {"title": "song title@alternate title", "alternate_title": "alternate title", "authors": "The Author", "ccli_number": "", "copyright": ""}, "fromPlugin": True, "capabilities": [2, 1, 5, 8, 9, 13, 22], "backgroundAudio": [], "isThemeOverwritten": False,
            "slides": [{"tag": "V1", "title": "Song Title", "selected": True, "text": "test text", "html": "lyrics 1", "chords": "lyrics 1", "footer": "Song Title<br/>    Written by:&nbsp;The Author<br/>"}, {"tag": "V1", "title": "Song Title", "selected": False, "text": "next text", "html": "lyrics 2", "chords": "lyrics 2", "footer": "Song Title<br/>    Written by:&nbsp;The Author<br/>"}], "id": "d61e5b58-530d-11f0-9697-6045cba385ca"
        }

        mockTCPConnector = MagicMock()
        mockRequest = _make_mock_request(data)

        obj.emit = AsyncMock()

        with (
            _mock_poll(poll_results),
            patch.multiple(
                'aiohttp',
                TCPConnector = mockTCPConnector,
                request = mockRequest
        )):
            await obj._loop_once()

        obj.emit.assert_called_once()
        slide_dict = obj.emit.call_args[0][0].to_dict()
        self.assertEqual(slide_dict['shapes'][0]['text'], 'test text')

    async def test_blank(self):
        await self._test_blank_types({'blank': True})
    async def test_theme(self):
        await self._test_blank_types({'blank': False, 'theme': True})
    async def test_display(self):
        await self._test_blank_types({'blank': False, 'theme': False,'display': True})

    async def _test_blank_types(self, results):
        ctx = MagicMock()

        cfg = openlp.OpenLPCapture.config({})
        obj = openlp.OpenLPCapture(ctx=ctx, cfg=cfg)

        mockTCPConnector = MagicMock()
        mockRequest = MagicMock()

        obj.emit = AsyncMock()

        with (
            _mock_poll(results),
            patch.multiple(
                'aiohttp',
                TCPConnector = mockTCPConnector,
                request = mockRequest
        )):
            await obj._loop_once()

        mockTCPConnector.assert_not_called()
        mockRequest.assert_not_called()
        obj.emit.assert_called_once()
        slide_dict = obj.emit.call_args[0][0].to_dict()
        self.assertEqual(slide_dict['shapes'], [])

    async def test_image(self):
        ctx = MagicMock()

        cfg = openlp.OpenLPCapture.config({})
        obj = openlp.OpenLPCapture(ctx=ctx, cfg=cfg)

        poll_results = {
                'counter': 4, 'service': 0, 'slide': 0, 'item': 'a121176e-5318-11f0-9697-6045cba385ca', 'twelve': True, 'blank': False, 'theme': False, 'display': False, 'version': 3, 'isSecure': False, 'chordNotation': 'english'
        }

        data = {
                'title': 'IMG_3685.heif',
                'name': 'images',
                'type': 2,
                'footer': [], 'audit': '',
                'notes': '',
                'data': {},
                'fromPlugin': True,
                'capabilities': [3, 1, 5, 6, 17, 21, 26],
                'slides': [{'tag': 1, 'title': 'an_image_file.heif', 'selected': True, 'img': 'data:image/heif;base64,'}],
                'id': 'a121176e-5318-11f0-9697-6045cba385ca',
        }

        mockTCPConnector = MagicMock()
        mockRequest = _make_mock_request(data)

        obj.emit = AsyncMock()

        with (
            _mock_poll(poll_results),
            patch.multiple(
                'aiohttp',
                TCPConnector = mockTCPConnector,
                request = mockRequest
        )):
            await obj._loop_once()

        obj.emit.assert_called_once()
        slide_texts = obj.emit.call_args[0][0].to_texts()
        self.assertEqual(slide_texts, [])


if __name__ == "__main__":
    unittest.main()
