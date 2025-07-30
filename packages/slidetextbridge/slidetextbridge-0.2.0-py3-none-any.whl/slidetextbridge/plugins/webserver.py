'''
Send text through HTTP
'''

import logging
from aiohttp import web
from slidetextbridge.core import config
from . import base

_DEFAULT_INDEX_HTML = '''
<!doctype html>
<html>
    <header>
        <script src="{uri_script}"></script>
        <link rel='stylesheet' href='{uri_style}' />
    </header>
    <body>
        <div class='text' id='placeholder'>
        </div>
    </body>
</html>
'''.strip()

_DEFAULT_SCRIPT_JS = '''
function get_appropriate_ws_url(extra_url) {
    var pcol;
    var u = document.URL;
    if (u.substring(0, 5) === "https") {
        pcol = "wss://";
        u = u.substr(8).split("/")[0];
    } else {
        pcol = "ws://";
        if (u.substring(0, 4) === "http")
            u = u.substr(7).split("/")[0];
    }
    return pcol + u + "/" + extra_url;
}

function text_to_html(text) {
    return text.replace(/[&<>"']/g, function (c) {
        return ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
        })[c];
    }).replace(/\\n/g, "<br/>");
}

let ws_failed = 0;
function connect_ws() {
    let url = get_appropriate_ws_url("ws/text");
    console.log("Connecting to", url);
    ws = new WebSocket(url);
    ws.onmessage = function(msg) {
        ws_failed = 0;
        console.log("Received:", msg.data);
        e = document.getElementById("placeholder");
        h = text_to_html(msg.data);
        console.log("HTML:", h);
        e.innerHTML = h;
    };
    ws.onclose = function() {
        ws_failed += 1;
        setTimeout(connect_ws, ws_failed < 6 ? ws_failed * 500 : 3000);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    connect_ws();
});
'''

_DEFAULT_STYLE_CSS = '''
body {
  font-family: sans-serif;
}
'''

class WebServerEmitter(base.PluginBase):
    '''
    HTTP server to send text through HTTP
    '''
    @classmethod
    def type_name(cls):
        return 'webserver'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('host', type=str, default='localhost')
        cfg.add_argment('port', type=int, default=8080)
        cfg.add_argment('uri_index', type=str, default='/index.html')
        cfg.add_argment('uri_script', type=str, default='/script.js')
        cfg.add_argment('uri_style', type=str, default='/style.css')
        cfg.add_argment('index_html', type=str, default=_DEFAULT_INDEX_HTML)
        cfg.add_argment('script_js', type=str, default=_DEFAULT_SCRIPT_JS)
        cfg.add_argment('style_css', type=str, default=_DEFAULT_STYLE_CSS)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'webserver({self.cfg.location})')
        self.app = None
        self.clients = set()
        self._last_text = None
        self.connect_to(cfg.src)

    def _fmt(self, text):
        return text \
                .replace('{uri_script}', self.cfg.uri_script) \
                .replace('{uri_style}', self.cfg.uri_style)

    async def _handle_index(self, request):
        # pylint: disable=unused-argument
        return web.Response(text=self._fmt(self.cfg.index_html), content_type='text/html')

    async def _handle_script(self, request):
        # pylint: disable=unused-argument
        return web.Response(text=self._fmt(self.cfg.script_js), content_type='text/javascript')

    async def _handle_style(self, request):
        # pylint: disable=unused-argument
        return web.Response(text=self._fmt(self.cfg.style_css), content_type='text/css')

    async def _handle_ws(self, request):
        # pylint: disable=unused-argument
        self.logger.info('Starting %s remote=%s', request.rel_url, request.remote)
        try:
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            self.clients.add(ws)

            if self._last_text:
                await self._send_text(ws, self._last_text)

            async for _ in ws:
                pass
        except Exception as e:
            self.logger.error('%s: Failed to process ws message. %s', request.remote, e)
        finally:
            self.clients.discard(ws)

        self.logger.info('Closing %s remote=%s', request.rel_url, request.remote)
        return ws

    async def initialize(self):
        self.app = web.Application()
        self.app.add_routes([
            web.get('/', self._handle_index),
            web.get(self.cfg.uri_index, self._handle_index),
            web.get(self.cfg.uri_script, self._handle_script),
            web.get(self.cfg.uri_style, self._handle_style),
            web.get('/ws/text', self._handle_ws),
        ])
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.cfg.host, self.cfg.port)
        await site.start()
        self.logger.info('Listening on %s:%d', self.cfg.host, self.cfg.port)

    async def update(self, slide, args):
        if not slide:
            text = ''
        elif isinstance(slide, str):
            text = slide
        else:
            text = str(slide)

        self._last_text = text
        for ws in self.clients:
            await self._send_text(ws, text)

    async def _send_text(self, ws, text):
        try:
            await ws.send_str(text)
        except Exception as e:
            self.logger.warning('Failed to send text to ws. %s', e)
