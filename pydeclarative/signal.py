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


import asyncio
import pdb
import logging
import weakref
from functools import partial
import wrapt


class IndirectWeakProxy(wrapt.ObjectProxy):
    def __init__(self, target, indirect_target=None, callback=None):
        super().__init__(target)
        if indirect_target is not None:
            self.indirect_target = weakref.ref(indirect_target, self.indirect_callback)
        else:
            self.indirect_target = None
        self.callback = callback

    def indirect_callback(self, wr):
        self.indirect_target = None
        if self.callback is not None:
            self.callback(self)

    def __call__(self, *args, **kwargs):
        return self.__wrapped__(*args, **kwargs)


class Signal:
    def __init__(self):
        self.connections = set()

    def connect(self, handler, queue=False):
        from .engine import Scope
        logger = logging.getLogger()
        if queue:
            conn = QueuedConnection(queue, handler)
        else:
            conn = handler
        if isinstance(handler, partial) and len(handler.args) == 1 and isinstance(handler.args[0], Scope):
            node = handler.args[0].__dict__['node'].real_self
            logger.info(f'Connecting to slot: {handler.func.__name__} in node: {node}')
            def callback(p):
                logger.info(f'Removing slot from dead scope: {conn}')
                self.connections.discard(p)
            conn = IndirectWeakProxy(conn, node, callback)
        self.connections.add(conn)
        return conn

    def disconnect(self, conn):
        self.connections.remove(conn)

    def disconnect_all(self):
        self.connections.clear()

    def __call__(self, *args, **kwargs):
        for handler in self.connections:
            handler(*args, **kwargs)


class QueuedConnection:
    def __init__(self, queue, handler):
        self.queue = queue
        self.handler = handler

    def __call__(self, *args, **kwargs):
        self.queue.append(self.handler, args, kwargs)


class SignalQueue:
    def __init__(self):
        self.event = asyncio.Event()
        self.queue = []

    async def wait_for_signal(self):
        if not self.queue:
            self.event.clear()
            await self.event.wait()
        while self.queue:
            handler, args, kwargs = self.queue.pop(0)
            handler(*args, **kwargs)

    def append(self, handler, args, kwargs):
        self.queue.append(( handler, args, kwargs ))
        self.event.set()

    def __iter__(self):
        return iter(self.queue)
