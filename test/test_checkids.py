from pydeclarative.htmlwidgets import *
from pydeclarative.checkids import *
import ast
import pytest
import textwrap
import inspect


def test00_get_target_names():
    target = ast.Tuple([ ast.Name('a'), ast.Name('b') ])
    assert get_target_names(target) == [ 'a', 'b' ]


def test01_get_target_names():
    target = ast.List([ ast.Name('a'), ast.Name('b') ])
    assert get_target_names(target) == [ 'a', 'b' ]


def test02_get_target_names():
    target = ast.Name('foobar')
    assert get_target_names(target) == [ 'foobar' ]


def test03_checkids():
    class root(Item):
        a = 1
        b = 2
    checkids(root)


def test04_checkids():
    class root(Item):
        a = 1
        a = 2
    with pytest.raises(NameError, match='Duplicate id'):
        checkids(root)


def test05_checkids():
    class root(Item):
        class _nested(Item):
            a = 1
            a = 2
    with pytest.raises(NameError, match='Duplicate id'):
        checkids(root)


def test06_checkids():
    class root(Item):
        class _nested:
            a = 1
            a = 2
    with pytest.raises(NameError, match='Duplicate id'):
        checkids(root)


def test06_checkids():
    class root(Item):
        class _nested:
            class _doubleNested:
                a = 1
                a = 2
    with pytest.raises(NameError, match='Duplicate id'):
        checkids(root)


def test07_get_names_in_order():
    class base:
        a = 1
        b = 2
        c = 3
    class deriv(base):
        d = 7
        c = 4
        class g:
            pass
        b = 5
        a = 6
        def f():
            pass
        async def h():
            pass
        pass
    res = get_names_in_order(deriv)
    assert list(res.keys()) == [ 'a', 'b', 'c', 'd', 'g', 'f', 'h' ]


def test08_get_target_names_as_ordered_dict():
    target = ast.Tuple([ ast.Name('a'), ast.Name('b') ])
    assert get_target_names_as_ordered_dict(target) == { 'a': None, 'b': None }


def test09_get_target_names_as_ordered_dict():
    target = ast.List([ ast.Name('a'), ast.Name('b') ])
    assert get_target_names_as_ordered_dict(target) == { 'a': None, 'b': None }


def test10_get_target_names_as_ordered_dict():
    target = ast.Name('foobar')
    assert get_target_names_as_ordered_dict(target) == { 'foobar': None }


def test11_get_children_in_order():
    class base(Item):
        class a(Item):
            pass
        class b(Item):
            pass
        class c(Item):
            pass
    class deriv(base):
        class c(Item):
            pass
        class b(Item):
            pass
        class a(Item):
            pass
    assert get_children_in_order(deriv) == [ deriv.a, deriv.b, deriv.c ]