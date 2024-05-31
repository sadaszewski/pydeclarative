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
import ast
import logging
import pdb
from textwrap import dedent
from functools import reduce


def get_target_names(target):
    if isinstance(target, ast.Tuple) or isinstance(target, ast.List):
        return [ el.id for el in target.elts ]
    else:
        return [ target.id ]


def checkids(item, trace=[]):
    if hasattr(item, '__pydeclarative_checkids_ok__'):
        return
    logger = logging.getLogger()
    if isinstance(item, type):
        top = ast.parse(dedent(inspect.getsource(item)))
        if len(top.body) != 1 or not isinstance(top.body[0], ast.ClassDef):
            raise TypeError(f'Expected {item} to be a single class, trace: {".".join(trace)}')
        cls = top.body[0]
    elif isinstance(item, ast.ClassDef):
        cls = item
    else:
        raise TypeError(f'Expected {item} to be a single class, trace: {".".join(trace)}')
    used_names = set()
    trace = trace + [ cls.name ]
    for stmt in cls.body:
        names = []
        if isinstance(stmt, ast.ClassDef):
            names = [ stmt.name ]
            checkids(stmt, trace)
        elif isinstance(stmt, ast.Assign):
            names = reduce(list.__add__, [ get_target_names(t) for t in stmt.targets ])
        elif isinstance(stmt, ast.FunctionDef) or isinstance(stmt, ast.AsyncFunctionDef):
            names = [ stmt.name ]
        elif isinstance(stmt, ast.Pass):
            pass
        else:
            logger.warn(f'Unexpected statement type: {stmt.__class__.__name__} detected in {".".join(trace)}')
        for n in names:
            if n in used_names:
                raise NameError(f'Duplicate id: {n} detected in {".".join(trace)}')
            used_names.add(n)
    item.__pydeclarative_checkids_ok__ = True


def get_target_names_as_ordered_dict(target):
    if isinstance(target, ast.Tuple) or isinstance(target, ast.List):
        return { el.id: None for el in target.elts }
    else:
        return { target.id: None }


def get_names_in_order(item):
    logger = logging.getLogger()
    res = dict()
    if item == object:
        return res
    for b in item.__bases__:
        res.update(get_names_in_order(b))
    # pdb.set_trace()
    top = ast.parse(dedent(inspect.getsource(item)))
    if len(top.body) != 1 or not isinstance(top.body[0], ast.ClassDef):
        raise TypeError(f'Expected {item} to be a single class')
    cls = top.body[0]
    for stmt in cls.body:
        if isinstance(stmt, ast.ClassDef):
            res.update({ stmt.name: None })
        elif isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                res.update(get_target_names_as_ordered_dict(t))
        elif isinstance(stmt, ast.FunctionDef) or isinstance(stmt, ast.AsyncFunctionDef):
            res.update({ stmt.name: None })
        elif isinstance(stmt, ast.Pass):
            pass
        else:
            logger.warn(f'Unexpected statement type: {stmt.__class__.__name__} detected in {item}')
    return res


def get_children_in_order(item):
    if hasattr(item, '__pydeclarative_children_in_order__'):
        return item.__pydeclarative_children_in_order__
    from .htmlwidgets import Item
    res = get_names_in_order(item)
    children = { k: v for k, v in inspect.getmembers(item) if inspect.isclass(v) and issubclass(v, Item) }
    res = [ children[n] for n in res if n in children ]
    item.__pydeclarative_children_in_order__ = res
    return res
