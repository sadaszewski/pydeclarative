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


import inspect
from .htmlwidgets import Item
from contextvars import ContextVar
from collections import defaultdict
from functools import partial
import uuid
import logging
import asyncio
import copy
import pdb
import weakref
from .signal import Signal
from .checkids import checkids, \
    get_children_in_order


CURRENT_DEPENDENT = ContextVar('CURRENT_DEPENDENT')
CURRENT_DEPENDENT.set(None)


class PropertyDict(defaultdict):
    def __init__(self, node):
        self.node = weakref.proxy(node.real_self)

    def __missing__(self, key):
        self[key] = value = Property(self.node, key, value=None, binding=None)
        return value
    

def not_equal(a, b):
    try:
        return (a != b)
    except Exception:
        return True


class Property:
    def __init__(self, node, name, *, value, binding):
        self.node = weakref.proxy(node.real_self)
        self.name = name
        self.value = value
        self.binding = binding
        self.dependents = weakref.WeakSet()
        self.dependencies = weakref.WeakSet()
        self.is_computing = False
        self.compute_counter = 0
        self.change_signal = Signal()

    def compute(self):
        if self.is_computing:
            raise RuntimeError('Circular dependency detected in ' + self.name)
        if self.binding:
            self.is_computing = True
            token = CURRENT_DEPENDENT.set(self)
            try:
                # pdb.set_trace()
                value = self.binding(Scope(self.node))
                self.compute_counter += 1
                if not_equal(value, self.value):
                    self.value = value
                    if self.name == 'html' and self.node.is_loaded:
                        self.node.engine.html_changed(self.node.real_self)
                    for dep in self.dependents:
                        dep.compute()
                    CURRENT_DEPENDENT.set(None)
                    self.is_computing = False
                    self.change_signal()
            finally:
                CURRENT_DEPENDENT.reset(token)
                self.is_computing = False
        return self.value

    def __repr__(self):
        return f'Property(name={self.name}, dependents={len(self.dependents)}, dependencies={len(self.dependencies)})'
    
    def clear_dependencies(self):
        for dep in self.dependencies:
            dep.dependents.remove(self)
        self.dependencies.clear()


class Binding:
    def __init__(self, binding):
        if isinstance(binding, Partial):
            self.binding = binding.func
        else:
            self.binding = binding


class LazyBinding:
    def __init__(self, compute_fn):
        self.compute_fn = compute_fn

    def compute(self, scope):
        return Binding(self.compute_fn(scope)).binding


class Partial(partial):
    pass


class Scope:
    def __init__(self, node):
        self.node = weakref.proxy(node.real_self)

    def find_in_children(self, name):
        Q = list(self.node.children)
        while Q:
            ch = Q.pop(0)
            if ch.id == name or name in ch.alt_ids:
                return ch
            Q += ch.children
        return None

    def find_in_parents(self, name):
        res = self.node.parent
        while res:
            if res.id == name or name in res.alt_ids:
                return res
            ch = Scope(res).find_in_children(name)
            if ch is not None:
                return ch
            res = res.parent
        return None

    def getitem_helper(self, name, exception_class=KeyError):
        if 'node' not in self.__dict__ or self.node is None:
            raise ValueError('This scope has no associated node')
        if name == 'parent':
            if self.node.parent is None:
                raise ValueError('There is no parent scope for current scope')
            return Scope(self.node.parent)
        if name in self.node.functions:
            return Partial(self.node.functions[name], Scope(self.node.real_self))
        if name in self.node.properties:
            if self.node.properties[name].compute_counter == 0:
                self.node.properties[name].compute()
            if CURRENT_DEPENDENT.get():
                CURRENT_DEPENDENT.get().dependencies.add(self.node.properties[name])
                self.node.properties[name].dependents.add(CURRENT_DEPENDENT.get())
            return self.node.properties[name].value
        res = self.find_in_children(name) or self.find_in_parents(name)
        if res:
            return Scope(res)
        # pdb.set_trace()
        raise exception_class(f'Reference {name} not found in the scope of {self.node}')

    def __getattr__(self, name):
        return self.getitem_helper(name, exception_class=AttributeError)

    def __setattr__(self, name, value):
        if name == 'node':
            super().__setattr__(name, value)
            return
        if name in self.node.properties:
            prop = self.node.properties[name]
            if isinstance(value, Binding):
                if prop.binding != value.binding:
                    prop.clear_dependencies()
                    prop.value = None
                    prop.compute_counter = 0
                    prop.binding = value.binding
                    # pdb.set_trace()
                    prop.compute()
            else:
                prop.clear_dependencies()
                prop.binding = None
                if not_equal(prop.value, value):
                    prop.value = value
                    if name == 'html' and self.node.is_loaded:
                        self.node.engine.html_changed(self.node.real_self)
                    for dep in prop.dependents:
                        dep.compute()
                    prop.change_signal()
            return
        raise TypeError('Cannot assign to: ' + name)

    def __getitem__(self, name):
        return self.getitem_helper(name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def get(self, name, default_value=None):
        try:
            return self.getitem_helper(name)
        except NameError:
            return default_value

    def find_uuid(self, uuid, return_node=False):
        Q = [ self.node ]
        while Q:
            node = Q.pop(0)
            if node.uuid == uuid:
                return (node if return_node else Scope(node))
            for ch in node.children:
                Q.append(ch)
        return None


def get_engine(scope):
    return scope.__dict__['node'].engine


def get_node(scope_or_node):
    if isinstance(scope_or_node, Scope):
        return scope_or_node.__dict__['node']
    return scope_or_node


class Node:
    def __init__(self, engine, item, id, parent=None):
        self.engine = weakref.proxy(engine)
        self.item = item
        self.id = id
        self.alt_ids = [ c.__name__ for c in inspect.getmro(item) ]
        self.parent = weakref.proxy(parent.real_self) if parent is not None else None
        self.properties = PropertyDict(self)
        self.children = []
        self.functions = {}
        self.uuid = str(uuid.uuid4())
        self.dom_html = None
        self.is_loaded = False

    @property
    def real_self(self):
        return self

    def add_child(self, node, index=None):
        node.parent = weakref.proxy(self)
        if index is not None:
            self.children.insert(index, node)
        else:
            self.children.append(node)

    def init_static_properties(self, provided_values={}):
        attrs = [ (k, v) for k, v in inspect.getmembers(self.item) \
            if not inspect.isclass(v) and \
                not isinstance(v, property) and \
                not inspect.isfunction(v) and \
                not isinstance(v, Binding) and \
                not isinstance(v, LazyBinding) and \
                not (k.startswith('__') and k.endswith('__')) ]
        for k, v in attrs:
            if not inspect.isfunction(v):
                self.properties[k].value = copy.deepcopy(v) \
                    if not k in provided_values else provided_values[k]
                self.properties[k].binding = None
        for ch in self.children:
            ch.init_static_properties()

    def init_dynamic_properties(self):
        attrs = [ (k, v) for k, v in inspect.getmembers(self.item) \
            if (isinstance(v, property) or isinstance(v, Binding) or isinstance(v, LazyBinding)) and \
                not (k.startswith('__') and k.endswith('__')) ]
        for k, v in attrs:
            self.properties[k].value = None
            self.properties[k].binding = v.fget \
                if isinstance(v, property) else v.binding \
                if isinstance(v, Binding) else v.compute(Scope(self))
        for ch in self.children:
            ch.init_dynamic_properties()

    def compute_dynamic_properties(self):
        for prop in self.properties.values():
            if prop.binding is not None:
                prop.compute()
        for ch in self.children:
            ch.compute_dynamic_properties()

    def init_functions(self):
        attrs = [ (k, v) for k, v in inspect.getmembers(self.item) \
            if inspect.isfunction(v) and \
                not (k.startswith('__') and k.endswith('__')) ]
        for k, v in attrs:
            self.functions[k] = v
        for ch in self.children:
            ch.init_functions()

    def connect_signals(self):
        for k in self.functions.keys():
            if k.startswith('on_') and k.endswith('_changed'):
                name = k[3:-8]
                self.properties[name].change_signal.connect(Scope(self)[k])
            elif k.startswith('on_'):
                name = k[3:]
                Scope(self)[name].connect(Scope(self)[k])
        for ch in self.children:
            ch.connect_signals()

    def init_members(self, provided_values={}):
        self.init_static_properties(provided_values)
        self.init_functions()
        self.init_dynamic_properties()
        self.connect_signals()
        self.compute_dynamic_properties()

    def __repr__(self):
        return 'Node(id=' + self.id + ', parent=' + (self.parent.id if self.parent else 'None') + ')'

    def bfs_list(self):
        res = [ self ]
        i = 0
        while i < len(res):
            entry = res[i]
            for ch in entry.children:
                res.append(ch)
            i += 1
        return res


class DeclarativeEngine:
    def __init__(self):
        self.node_created = Signal()
        self.html_changed = Signal()
        self.node_removed = Signal()
        self.custom_message = Signal()
        self.tasks = set()

    def load(self, item, is_root=False, parent=None, provided_values={}, index=None):
        logger = logging.getLogger()
        checkids(item)
        children = get_children_in_order(item)
        logger.info(f'children: {children}')
        if parent is not None:
            parent = get_node(parent)
        node = Node(self, item, item.__name__, parent=parent)
        if parent is not None:
            parent.add_child(node, index=index)
        for ch in children:
            node.add_child(self.load(ch))
        if is_root:
            node.init_members(provided_values)
            Q = node.bfs_list()
            for entry in Q:
                entry.is_loaded = True
                logger.info('node_created() ' + entry.uuid + ' ' + str(Scope(entry).html))
                self.node_created(entry, index)
            for entry in Q:
                loaded = entry.properties.get('loaded')
                if loaded:
                    try:
                        loaded.value()
                    except Exception as e:
                        self.send_global_message('backend_exception', dict(exception=str(e)))
        return node

    def unload(self, node, suppress_signal=False):
        Q = reversed(node.bfs_list())
        for entry in Q:
            unloaded = entry.properties.get('unloaded')
            if unloaded:
                try:
                    unloaded.value()
                except Exception as e:
                    self.send_global_message('backend_exception', dict(exception=str(e)))
        if node.parent:
            node.parent.children.remove(node)
        if not suppress_signal:
            self.node_removed(node.uuid)

    def handle_dom_event(self, event, root_node):
        logger = logging.getLogger()
        logger.info('handle_dom_event() ' + str(event))
        node = Scope(root_node).find_uuid(event['uuid'], return_node=True)
        if node is None:
            logger.warning('Node removed before DOM event could be delivered: ' + event['uuid'])
        else:
            scope = Scope(node)
            scope.handle_dom_event(event)

    def create_task(self, aw):
        res = asyncio.create_task(aw)
        res.add_done_callback(self.tasks.discard)
        self.tasks.add(res)
        return res

    def cancel_tasks(self):
        for task in self.tasks:
            task.cancel()

    def send_custom_message(self, target, message_type, message):
        node = get_node(target)
        self.custom_message(weakref.proxy(node.real_self), message_type, message)

    def send_global_message(self, message_type, message):
        logger = logging.getLogger()
        logger.info(f'send_global_message() {message_type} {message}')
        self.custom_message(None, message_type, message)

    def execute_js(self, js):
        self.send_global_message('execute_js', dict(js=js))
