import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from slidetextbridge.plugins import obsws

class TestObsWsEmitter(unittest.IsolatedAsyncioTestCase):

    def test_type_name(self):
        self.assertEqual(obsws.ObsWsEmitter.type_name(), 'obsws')

    def test_config(self):
        cfg_data = {'url': 'ws://192.0.2.1:4455/', 'password': 'pw', 'source_name': 'TestSource'}
        cfg = obsws.ObsWsEmitter.config(cfg_data)
        self.assertEqual(cfg.url, 'ws://192.0.2.1:4455/')
        self.assertEqual(cfg.password, 'pw')
        self.assertEqual(cfg.source_name, 'TestSource')


    @patch('simpleobsws.WebSocketClient', autospec=True)
    async def test_connect_and_update(self, MockWebSocketClient):
        ctx = MagicMock()

        cfg_src = 'dummy'
        cfg_url = 'ws://localhost:4455/'
        cfg_password = 'secret'
        cfg_src_name = 'test-source-name'
        cfg = obsws.ObsWsEmitter.config({
                'src': cfg_src,
                'url': cfg_url,
                'password': cfg_password,
                'source_name': cfg_src_name
        })

        mock_ws = AsyncMock()
        mock_res = MagicMock()
        MockWebSocketClient.return_value = mock_ws
        mock_ws.connect.return_value = None
        mock_ws.wait_until_identified.return_value = True
        mock_ws.call.return_value = mock_res
        mock_res.ok.return_value = True
        mock_res.responseData = {'status': 'ok'}

        obj = obsws.ObsWsEmitter(ctx=ctx, cfg=cfg)
        ctx.get_instance.assert_called_once_with(name=cfg_src)

        await obj.update('test text', args=None)

        MockWebSocketClient.assert_called_with(url=cfg_url, password=cfg_password)
        mock_ws.connect.assert_awaited()
        mock_ws.call.assert_awaited_with(obsws.simpleobsws.Request(
            'SetInputSettings',
            {
                'inputName': cfg_src_name,
                'inputSettings': {'text': 'test text'},
            }
        ))

if __name__ == '__main__':
    unittest.main()
