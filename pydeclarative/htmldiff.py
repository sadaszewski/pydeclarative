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


import bs4
import pdb


def htmldiff(elem_new, elem_old):
    res=[]
    if isinstance(elem_new, str) ^ isinstance(elem_old, str):
        if isinstance(elem_new, str):
            res.append(dict(action='replace_element', text=str(elem_new)))
        else:
            res.append(dict(action='replace_element', html=str(elem_new)))
        return res

    if isinstance(elem_new, str) and elem_new == elem_old:
        return res

    if isinstance(elem_new, str) and elem_new != elem_old:
        res.append(dict(action='replace_element', text=str(elem_new)))
        return res

    if ('data-content-item' in elem_new.attrs) ^ ('data-content-item' in elem_old.attrs):
        raise ValueError('Expected content items to match')

    set_attrs = {}
    for k in set(elem_new.attrs.keys()).intersection(elem_old.attrs.keys()):
        if elem_new.attrs[k] != elem_old.attrs[k]:
            set_attrs[k] = elem_new.attrs[k]
    for k in set(elem_new.attrs.keys()).difference(elem_old.attrs.keys()):
        set_attrs[k] = elem_new.attrs[k]
    if set_attrs:
        res.append(dict(action='set_attrs', attrs=set_attrs))

    remove_attrs = []
    for k in set(elem_old.attrs.keys()).difference(elem_new.attrs.keys()):
        remove_attrs.append(k)
    if remove_attrs:
        res.append(dict(action='remove_attrs', attrs=remove_attrs))

    if 'data-content-item' in elem_new.attrs:
        return res

    if elem_new.name != elem_old.name:
        res.append(dict(action='replace_element', html=str(elem_new)))
        return res

    remove_children = list(range(len(elem_new.contents), len(elem_old.contents)))
    if remove_children:
        res.append(dict(action='remove_children', indices=remove_children))
    for i in range(len(elem_old.contents), len(elem_new.contents)):
        add_child = dict(action='add_child', index=i)
        if isinstance(elem_new.contents[i], str):
            add_child.update(dict(text=str(elem_new.contents[i])))
        else:
            add_child.update(dict(html=str(elem_new.contents[i])))
        res.append(add_child)
    for i in range(0, min(len(elem_new.contents), len(elem_old.contents))):
        recipe = htmldiff(elem_new.contents[i], elem_old.contents[i])
        if recipe:
            res.append(dict(action='update_child', index=i, recipe=recipe))
    return res


def applydiff(elem_old, recipe):
    raise NotImplementedError
