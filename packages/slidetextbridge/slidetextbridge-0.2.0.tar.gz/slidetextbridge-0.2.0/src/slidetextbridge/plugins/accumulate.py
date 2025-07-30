'''
Accumulate plugins
'''

import os
import logging
from . import text_filters
from . import debug_helper

logger = logging.getLogger(__name__)

_is_win = os.name.startswith('nt')

plugin_classes = []

plugin_classes.append(text_filters.TextLinebreakFilter)
plugin_classes.append(text_filters.RegexFilter)
plugin_classes.append(debug_helper.StdoutEmitter)

try:
    from . import obsws
    plugin_classes.append(obsws.ObsWsEmitter)
except ImportError as e:
    logger.info('obsws is unsupported. %s', e)

if _is_win:
    try:
        from . import powerpoint
        plugin_classes.append(powerpoint.PowerPointCapture)
    except ImportError as e:
        logger.info('Microsoft PowerPoint is unsupported %s', e)

try:
    from . import impress
    plugin_classes.append(impress.ImpressCapture)
except ImportError as e:
    logger.info('LibreOffice is unsupported %s', e)

try:
    from . import openlp
    plugin_classes.append(openlp.OpenLPCapture)
except ImportError as e:
    logger.info('OpenLP is unsupported %s', e)

try:
    from . import jmespath_filter
    plugin_classes.append(jmespath_filter.JMESPathFilter)
except ImportError as e:
    logger.info('JMESPath filter is unsupported %s', e)

try:
    from . import webserver
    plugin_classes.append(webserver.WebServerEmitter)
except ImportError as e:
    logger.info('Web server is unsupported %s', e)

plugins = {cls.type_name(): cls for cls in plugin_classes}
