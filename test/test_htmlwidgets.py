from pydeclarative.engine import *
from pydeclarative.htmlwidgets import *
import bs4
import pytest


def test00_get_node():
    class MockItem:
        pass
    class MockEngine:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    assert get_node(Scope(node)) == node


def test01_get_engine():
    class MockItem:
        pass
    class MockEngine:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    assert get_engine(Scope(node)) == engine


def test02_has_property():
    from pydeclarative.htmlwidgets import has_property
    class MockItem:
        abc = 123
    class MockEngine:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    node.init_members()
    assert has_property(node, 'abc')
    assert not has_property(node, 'def')


def test03_add_standard_attributes():
    class MockItem(Item):
        css_style = dict(width='100px', height='100px')
        css_class = [ 'button', 'button-warning' ]
        disabled = True
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    root.init_members()
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert doc.attrs['class'] == 'button button-warning'
    assert doc.attrs['style'] == 'width: 100px; height: 100px;'
    assert doc.attrs['disabled'] == 'disabled'
    Scope(root).css_style = 'background-color: red;'
    Scope(root).css_class = 'form control'
    Scope(root).disabled = False
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert doc.attrs['class'] == 'form control'
    assert doc.attrs['style'] == 'background-color: red;'
    assert 'disabled' not in doc.attrs


def test04_elem_to_html():
    from pydeclarative.htmlwidgets import elem_to_html
    class MockScope:
        class node:
            properties = { 'disabled', 'css_class', 'css_style' }
        disabled = True
        css_class = [ 'button', 'button-warning' ]
        css_style = dict(width='100px', height='100px')
    elem = bs4.BeautifulSoup('<div />', 'xml').find()
    doc = bs4.BeautifulSoup(elem_to_html(MockScope, elem), 'xml').find()
    assert doc.attrs['class'] == 'button button-warning'
    assert doc.attrs['style'] == 'width: 100px; height: 100px;'
    assert doc.attrs['disabled'] == 'disabled'


def test05_delegate():
    def fun():
        pass
    d = Delegate(fun)
    assert d.delegate == fun


def test06_delegate():
    def fun():
        pass
    assert isinstance(delegate(fun), Delegate)


def test07_item():
    class MockItem(Item):
        pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert 'html' in root.properties
    assert 'handle_dom_event' in root.functions
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert doc.name == 'div'


def test07_div():
    class MockItem(Div):
        pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert 'html' in root.properties
    assert 'handle_dom_event' in root.functions
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert doc.name == 'div'


def test08_text_input():
    class MockItem(TextInput):
        pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert 'html' in root.properties
    assert 'handle_dom_event' in root.functions
    assert 'text' in root.properties
    assert 'placeholder' in root.properties
    assert 'input_type' in root.properties
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert doc.name == 'input'
    assert Scope(root).text == ''
    Scope(root).handle_dom_event(dict(event='value_changed', property_name='text', new_value='foobar'))
    assert Scope(root).text == 'foobar'
    with pytest.raises(ValueError, match='Unrecognized event'):
        Scope(root).handle_dom_event(dict(event='unknown_event'))


def test09_password_input():
    assert issubclass(PasswordInput, TextInput)
    assert PasswordInput.input_type == 'password'


def test10_text_output():
    class MockItem(TextOutput):
        pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert 'html' in root.properties
    assert 'handle_dom_event' in root.functions
    assert 'text' in root.properties
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert doc.name == 'div'
    assert len(list(doc.children)) == 0
    Scope(root).text = 'foobar'
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert len(list(doc.children)) == 1
    assert list(doc.children)[0].text == 'foobar'


def test11_button():
    on_clicked_was_called = False
    class MockItem(Button):
        def on_clicked(scope):
            nonlocal on_clicked_was_called
            on_clicked_was_called = True
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert 'html' in root.properties
    assert 'handle_dom_event' in root.functions
    assert 'text' in root.properties
    assert 'button_class' in root.properties
    assert 'is_outline_button' in root.properties
    doc = bs4.BeautifulSoup(Scope(root).html, 'xml').find()
    assert doc.name == 'button'
    assert len(list(doc.children)) == 1
    assert list(doc.children)[0].text == 'Button'
    assert Scope(root).button_class == 'primary'
    assert Scope(root).is_outline_button == False
    Scope(root).handle_dom_event(dict(event='native_event', event_name='clicked'))
    assert on_clicked_was_called