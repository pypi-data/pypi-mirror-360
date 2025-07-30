'''
Get text from OpenLP
'''

import json
import asyncio
import logging
import aiohttp
import aiohttp.client_exceptions
import websockets
from slidetextbridge.core import config
from . import base


def _is_blank(poll):
    if poll['results']['blank']:
        return True
    if poll['results']['theme']:
        return True
    if poll['results']['display']:
        return True
    return False

def _filter_by_types(slide, item):
    item_type = item['type']
    if item_type == 1: # bibles songs custom
        return slide
    return None


class OpenLPCapture(base.PluginBase):
    '''
    Get text from OpenLP
    '''
    @classmethod
    def type_name(cls):
        return 'openlp'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg, has_src=False)
        cfg.add_argment('host', type=str, default='localhost')
        cfg.add_argment('port', type=int, default=4316)
        cfg.add_argment('port_ws', type=int, default=None)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'openlp({self.cfg.location})')

        self._conn = None
        self._conn_ws = None
        self._port_ws = None
        self._cache = {}
        if not self.cfg.port_ws:
            self.cfg.port_ws = self.cfg.port + 1

    async def _connect(self):
        if not self._conn:
            self._conn = aiohttp.TCPConnector()

    async def _connect_ws(self):
        url = f'ws://{self.cfg.host}:{self.cfg.port_ws:d}/poll'
        self._conn_ws = await websockets.connect(url)

    async def _disconnect(self):
        if self._conn:
            await self._conn.close()
            self._conn = None
        if self._conn_ws:
            self._conn_ws.close()
            self._conn_ws = None

    async def _olp_get(self, url):
        if not self._conn:
            await self._connect()
        if url[0] == '/':
            url = f'http://{self.cfg.host}:{self.cfg.port}{url}'
        async with aiohttp.request('GET', url, connector=self._conn) as res:
            txt = await res.text()
            return txt

    async def _olp_poll(self):
        if not self._conn_ws:
            await self._connect_ws()
        try:
            res = await self._conn_ws.recv()
        except Exception as e: # pylint: disable=W0718
            await self._conn_ws.close()
            self._conn_ws = None
            self.logger.warning('Failed to poll. %s', e)
        return json.loads(res)

    async def _cache_current_item(self):
        live_items = json.loads(await self._olp_get('/api/v2/controller/live-items'))
        self._cache[live_items['id']] = live_items

    async def _wait_and_get_text(self):
        while True:
            poll = await self._olp_poll()
            if not poll:
                return None
            if _is_blank(poll):
                return None
            poll_res = poll['results']
            item_uuid = poll_res['item']
            if item_uuid not in self._cache:
                try:
                    await self._cache_current_item()
                except aiohttp.client_exceptions.ClientOSError:
                    return None
            if item_uuid in self._cache:
                current_item = self._cache[item_uuid]
                break

        i_slide = poll_res['slide']
        return _filter_by_types(current_item['slides'][i_slide], current_item)

    async def _loop_once(self):
        obj = await self._wait_and_get_text()
        slide = OpenLPSlide(data = {'shapes': [obj] if obj else []}, parent=self)
        await self.emit(slide)

    async def initialize(self):
        asyncio.create_task(self._loop())

    async def _loop(self):
        last_error = None
        while True:
            try:
                await self._loop_once()
                last_error = None
            except Exception as e:
                error = str(e)
                if error != last_error:
                    self.logger.warning('%s', error)
                    last_error = error
                await asyncio.sleep(3)


class OpenLPSlide(base.SlideBase):
    'The slide class returned by OpenLPCapture'

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
            logger = self.parent.logger if self.parent else logging.getLogger('OpenLPSlide')
            logger.error('Failed to convert slide to texts. %s', e)
        return []

    def to_dict(self):
        return self._dict
