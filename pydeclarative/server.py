#
# Copyright (C) Stanislaw Adaszewski <s DOT adaszewski AT gmail DOT com>, 2024.
#
# This file is part of PyDeclarative.
#
# PyDeclarative is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# PyDeclarative is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more 
# details.
#
# You should have received a copy of the GNU Lesser General Public License along 
# with PyDeclarative. If not, see <https://www.gnu.org/licenses/>.
#


import websockets
import asyncio
from argparse import ArgumentParser
import importlib
import logging
from functools import partial
import json
import bs4
import pdb
import pathlib
import mimetypes
import os
import gc
import sys
import weakref
from .engine import DeclarativeEngine, \
    Scope
from .htmldiff import htmldiff
from .signal import SignalQueue


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('--module', type=str, required=True)
    parser.add_argument('--root', type=str, default='root')
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--port', type=int, default=8001)
    parser.add_argument('--logging-level', type=str, choices=logging._nameToLevel.keys(), default='INFO')
    parser.add_argument('--disable-htmldiff', action='store_true')
    return parser


class DoneCallback:
    def __init__(self, get_pending_tasks_fn, engine, root_node):
        self.get_pending_tasks_fn = get_pending_tasks_fn
        self.engine = engine
        self.root_node = root_node

    def __call__(self, *_):
        logger = logging.getLogger()
        for task in self.get_pending_tasks_fn():
            task.cancel()
            del task
        if self.engine:
            self.engine.cancel_tasks()
        # await asyncio.wait(set().union(pending).union(engine.tasks), return_when=asyncio.ALL_COMPLETED)
        logger.info('All tasks cancelled')
        if self.root_node:
            self.engine.unload(self.root_node)
            logger.info('Root node unloaded')
        if self.root_node:
            logger.info(f'# refs to root_node: {sys.getrefcount(self.root_node)}')
            logger.info(f'Referrers: {gc.get_referrers(self.root_node)}')
        self.get_pending_tasks_fn = None
        self.engine = None
        self.root_node = None


class Handler:
    def __init__(self, root_item, provided_values={}, disable_htmldiff=False):
        self.root_item = root_item
        self.provided_values = provided_values
        self.disable_htmldiff = disable_htmldiff

    async def __call__(self, websocket):
        gc.collect()
        logger = logging.getLogger()
        engine = DeclarativeEngine()
        pending = []
        root_node = None
        done_callback = DoneCallback(lambda: pending, engine, root_node)
        asyncio.current_task().add_done_callback(done_callback)
        queue = []
        dom_to_backend_message_counter = 0
        def node_created(node, index):
            node.dom_html = Scope(node).html
            queue.append(dict(event='node_created', uuid=node.uuid,
                parent=node.parent.uuid if node.parent else None,
                html=node.dom_html, index=index,
                dom_to_backend_message_counter=dom_to_backend_message_counter))    
        def html_changed(node):
            # pdb.set_trace()
            new_html = Scope(node).html
            logger.info('html_changed() ' + node.uuid + ' ' + new_html + ' ' + node.dom_html)
            if self.disable_htmldiff:
                diff = [ dict(action='replace_element', html=new_html) ]
            else:
                diff = htmldiff(
                    bs4.BeautifulSoup(new_html, 'xml').find(),
                    bs4.BeautifulSoup(node.dom_html, 'xml').find())
            node.dom_html = new_html
            if diff:
                queue.append(dict(event='html_changed', uuid=node.uuid,
                    diff=diff,
                    dom_to_backend_message_counter=dom_to_backend_message_counter))
                logger.info(diff)
        def node_removed(uuid):
            logger.info('node_removed() ' + uuid)
            queue.append(dict(event='node_removed', uuid=uuid,
                dom_to_backend_message_counter=dom_to_backend_message_counter))
        def custom_message(node, message_type, message):
            logger.info('custom_message() ' + (node.uuid if node else 'global') + ' ' + message_type)
            res = dict(message)
            if node:
                res['uuid']=node.uuid
            res.update(dict(event='custom_message', message_type=message_type,
                dom_to_backend_message_counter=dom_to_backend_message_counter))
            queue.append(res)
        signal_queue = SignalQueue()
        engine.node_created.connect(node_created, queue=signal_queue)
        engine.html_changed.connect(html_changed, queue=signal_queue)
        engine.node_removed.connect(node_removed, queue=signal_queue)
        engine.custom_message.connect(custom_message, queue=signal_queue)
        root_node = engine.load(self.root_item, is_root=True, provided_values=self.provided_values)
        done_callback.root_node = root_node
        del done_callback
        root_node = weakref.proxy(root_node)
        dom_event = asyncio.create_task(websocket.recv())
        signal_queue_event = asyncio.create_task(signal_queue.wait_for_signal())
        pending = [ dom_event, signal_queue_event ]
        while True:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                if task.exception():
                    logger.warning(task.exception())
                    engine.send_global_message('backend_exception', dict(exception=str(task.exception())))
            pending = list(pending)
            if dom_event in done:
                if dom_event.exception():
                    logger.info(type(dom_event.exception()))
                    break
                try:
                    dom_event = json.loads(dom_event.result())
                    logger.info(dom_event)
                    dom_to_backend_message_counter += 1
                    if dom_to_backend_message_counter != dom_event['dom_to_backend_message_counter']:
                        logger.warn('dom_to_backend_message_counter mismatch: %d vs %d' % \
                            (dom_to_backend_message_counter, dom_event['dom_to_backend_message_counter']))
                    engine.handle_dom_event(dom_event, root_node)
                except Exception as e:
                    logger.warning(e)
                    engine.send_global_message('backend_exception', dict(exception=str(e)))
                dom_event = asyncio.create_task(websocket.recv())
                pending.append(dom_event)
            if signal_queue_event in done:
                signal_queue_event = asyncio.create_task(signal_queue.wait_for_signal())
                pending.append(signal_queue_event)
            if queue:
                # await asyncio.sleep(1)
                payload = json.dumps(queue)
                queue = []
                await websocket.send(payload)


def process_request(path, headers):
    logger = logging.getLogger()
    def get_header(name):
        res = ','.join(headers.get_all(name))
        res = [ h.strip() for h in res.lower().split(',') ]
        return res
    if 'upgrade' not in get_header('Connection') or \
        'websocket' not in get_header('Upgrade'):
        # serve static file
        if path.endswith('/'):
            path = path + 'index.html'
        static_root = pathlib.Path(pathlib.Path(__file__).parent, '..', 'static').resolve()
        p = static_root.joinpath(path[1:]).resolve()
        logger.info(f'static_root: {static_root}')
        logger.info(f'path: {path}, p: {p}, relative: {p.is_relative_to(static_root)}')
        if not p.is_relative_to(static_root):
            return (403, {}, b'Access forbidden')
        if not os.path.exists(p):
            return (404, {}, b'File not found')
        with open(p, 'rb') as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(0)
            res = (200, {
                'Content-Type': mimetypes.guess_type(p)[0] or 'application/octet-stream',
                'Content-Length': size,
            }, f.read())
            # logger.info(f'res: {res}')
            return res
    else:
        #logger.info(f'process_request(), path: {path}')
        #for k, v in headers.items():
        #    logger.info(f'{k}: {v}')
        return None


async def main():
    parser = create_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging._nameToLevel[args.logging_level])
    logger = logging.getLogger()
    mod = importlib.import_module(args.module)
    root = getattr(mod, args.root)
    logger.info(f'root: {root}')
    async with websockets.serve(Handler(root, disable_htmldiff=args.disable_htmldiff), args.host, args.port, process_request=process_request):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
