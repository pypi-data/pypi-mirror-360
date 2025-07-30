'''
Main routine
'''

import argparse
import asyncio
import logging
import sys

from slidetextbridge.core.context import Context
from slidetextbridge.core import configtop

def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store', default='config.yaml')
    parser.add_argument('--strict', action='store_true')
    return parser.parse_args()

def _setup_ctx(cfgs):
    ctx = Context()
    from slidetextbridge.plugins import accumulate # pylint: disable=C0415
    for step in cfgs.steps:
        cls = accumulate.plugins[step.type]
        inst = cls(ctx=ctx, cfg=step)
        ctx.add_instance(inst)
    return ctx

async def _loop(ctx):
    await ctx.initialize_all()
    while True:
        tt = list(asyncio.all_tasks())
        tt.remove(asyncio.current_task())
        if not tt:
            break
        rr = await asyncio.gather(*tt, return_exceptions=True)
        for t, r in zip(tt, rr):
            if isinstance(r, Exception):
                logging.getLogger(__name__).error('%s: Unknown exception %s', t, r)
    logging.getLogger(__name__).info('All tasks are done.')

def main():
    'The entry point'
    try:
        logging.basicConfig(level=logging.INFO)
        args = _get_args()
        cfgs = configtop.load(args.config)
        ctx = _setup_ctx(cfgs)
    except Exception as e:
        logging.getLogger(__name__).error('Failed to start. %s', e)
        return 1

    try:
        asyncio.run(_loop(ctx))
    except KeyboardInterrupt:
        logging.getLogger(__name__).info('Interrupted')

    return 0

if __name__ == '__main__':
    sys.exit(main())
