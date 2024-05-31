from pydeclarative.engine import *
from functools import partial
import pytest


class MockNode:
    functions = {}
    @property
    def real_self(self):
        return self


def test00_property_dict():
    node = MockNode()
    d = PropertyDict(node)
    x = d['x']
    assert isinstance(x, Property)
    assert x.name == 'x'
    assert x.value is None
    assert x.binding is None


def test01_not_equal():
    assert not_equal(1, 2)


def test02_not_equal():
    class MockObject:
        def __eq__(self, other):
            raise TypeError('Cannot compare to other')
    o1 = MockObject()
    assert not_equal(o1, o1)


def test03_property():
    node = MockNode()
    p = Property(node, 'foobar', value=123, binding=None)
    assert p.compute() == 123
    

def _on_foobar_changed(scope):
    print('I am being called')
    pass


def test04_property(mocker):
    node = MockNode()
    mocked = mocker.patch('test_engine._on_foobar_changed')
    node.functions['on_foobar_changed'] = _on_foobar_changed
    p = Property(node, 'foobar', value=None, binding=lambda _: 123)
    p.change_signal.connect(partial(node.functions['on_foobar_changed'], None))
    assert p.value is None
    assert p.compute() == 123
    mocked.assert_called()
    assert CURRENT_DEPENDENT.get() is None


def test05_property():
    node = MockNode()
    _ = repr(Property(node, 'foobar', value=None, binding=None))


def test06_property():
    node = MockNode()
    p1 = Property(node, 'foobar', value=None, binding=None)
    p2 = Property(node, 'barbaf', value=None, binding=None)
    p1.dependencies.add(p2)
    p2.dependents.add(p1)
    assert next(iter(p1.dependencies)).__eq__(p2)
    assert next(iter(p2.dependents)).__eq__(p1)
    p1.clear_dependencies()
    assert len(p1.dependencies) == 0
    assert len(p2.dependents) == 0


def test07_binding():
    f = lambda scope: None
    b = Binding(f)
    assert isinstance(b, Binding)
    assert b.binding == f


def test08_binding():
    f = lambda scope: None
    b = Binding(Partial(f, None))
    assert b.binding == f


def test09_lazy_binding():
    lazy = LazyBinding(lambda scope: scope['foobar'])
    v = lazy.compute(dict(foobar=123))
    assert v == 123


def test10_scope():
    class MockEngine:
        pass
    class MockItem:
        foobar = 123
        def a_function(scope):
            pass
    engine = MockEngine()
    child = Node(engine, MockItem, 'child')
    parent = Node(engine, MockItem, 'parent')
    node = Node(engine, MockItem, 'node', parent=parent)
    node.add_child(child)
    node.functions['a_function'] = MockItem.a_function
    node.properties['foobar'] = Property(node, 'foobar', value=123, binding=None)
    scope = Scope(node)
    assert scope.find_in_children('child') == child
    assert scope.find_in_parents('parent') == parent
    assert get_node(scope.parent) == parent
    assert scope.a_function.func == MockItem.a_function
    assert get_node(scope.a_function.args[0]) == get_node(scope)
    assert scope.foobar == 123
    assert get_node(scope.child) == child
    assert get_node(scope.parent) == parent


def test11_scope():
    class MockEngine:
        pass
    class MockItem:
        foobar = 123
        def a_function(scope):
            pass
    engine = MockEngine()
    child = Node(engine, MockItem, 'child')
    parent = Node(engine, MockItem, 'parent')
    node = Node(engine, MockItem, 'node', parent=parent)
    node.add_child(child)
    node.functions['a_function'] = MockItem.a_function
    node.properties['foobar'] = Property(node, 'foobar', value=123, binding=None)
    scope = Scope(node)
    scope.foobar = 456
    assert scope.foobar == 456
    scope.foobar = Binding(lambda scope: 789)
    assert scope.foobar == 789
    with pytest.raises(TypeError):
        scope.non_existent = 1


def test12_node():
    class MockEngine:
        pass
    class MockItem:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    assert node.engine.__eq__(engine)
    assert node.item == MockItem
    assert node.id == 'node'
    assert node.parent is None
    assert node.properties == {}
    assert node.children == []
    assert node.functions == {}
    assert isinstance(node.uuid, str)
    assert node.dom_html is None
    assert node.is_loaded == False
    assert node.real_self == node


def test13_node():
    class MockEngine:
        pass
    class MockItem:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    child = Node(engine, MockItem, 'child')
    node.add_child(child)
    assert node.children[0] == child
    assert child.parent.__eq__(node)
    child2 = Node(engine, MockItem, 'child2')
    node.add_child(child2, index=0)
    assert node.children[0] == child2
    assert child2.parent.__eq__(node)


def test14_node():
    class MockEngine:
        pass
    class MockItem:
        abc = 123
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    child = Node(engine, MockItem, 'child')
    node.add_child(child)
    node.init_static_properties()
    for n in [node, child]:
        assert len(n.properties) == 1
        assert 'abc' in n.properties
        assert n.properties['abc'].name == 'abc'
        assert n.properties['abc'].value == 123
        assert n.properties['abc'].binding is None


def test15_node():
    class MockEngine:
        pass
    class MockItem:
        abc = 123
        @property
        def ghi(scope):
            return scope.abc * 2
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    child = Node(engine, MockItem, 'child')
    node.add_child(child)
    node.init_static_properties()
    child.properties['abc'].value = 456
    node.init_dynamic_properties()
    node.compute_dynamic_properties()
    assert node.properties['ghi'].value == 123 * 2
    assert child.properties['ghi'].value == 456 * 2


def test16_node():
    class MockEngine:
        pass
    class MockItem:
        def a_function(_):
            return 2 ** 16
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    child = Node(engine, MockItem, 'child')
    node.add_child(child)
    node.init_functions()
    assert node.functions['a_function'](None) == 2 ** 16
    assert child.functions['a_function'](None) == 2 ** 16


def test17_node():
    class MockEngine:
        pass
    class MockItem:
        abc = 123
        @property
        def ghi(scope):
            return scope.abc * 2
        def a_function(scope):
            return scope.ghi * 2
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    child = Node(engine, MockItem, 'child')
    node.add_child(child)
    node.init_members()
    assert node.functions['a_function'](Scope(node)) == 123 * 2 * 2
    assert child.functions['a_function'](Scope(child)) == 123 * 2 * 2


def test18_node():
    class MockEngine:
        pass
    class MockItem:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    assert isinstance(repr(node), str)


def test19_node():
    class MockEngine:
        pass
    class MockItem:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    child = Node(engine, MockItem, 'child')
    child2 = Node(engine, MockItem, 'child2')
    child3 = Node(engine, MockItem, 'child3')
    node.add_child(child)
    node.add_child(child2)
    child.add_child(child3)
    res = node.bfs_list()
    assert len(res) == 4
    assert res[0].__eq__(node)
    assert res[1].__eq__(child)
    assert res[2].__eq__(child2)
    assert res[3].__eq__(child3)


def test20_engine():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        pass
    engine = DeclarativeEngine()
    node = engine.load(MockItem, is_root=True)
    assert isinstance(node, Node)


def test21_engine():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        abc = 123
        class MockChild(Item):
            @property
            def ghi(scope):
                return scope.MockItem.abc * 2
    engine = DeclarativeEngine()
    node = engine.load(MockItem, is_root=True)
    assert node.children[0].properties['ghi'].value == 123 * 2


def test22_engine():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        pass
    engine = DeclarativeEngine()
    def on_node_created(entry, index):
        assert isinstance(entry, Node)
        assert index is None
        on_node_created.was_called = True
    on_node_created.was_called = False
    engine.node_created.connect(on_node_created)
    _ = engine.load(MockItem, is_root=True)
    assert on_node_created.was_called


def test23_engine():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        class MockChild(Item):
            pass
    engine = DeclarativeEngine()
    def on_node_removed(uuid):
        assert isinstance(uuid, str)
        assert uuid == child_uuid
        assert Scope(root).find_uuid(uuid) is None
        on_node_removed.was_called = True
    on_node_removed.was_called = False
    engine.node_removed.connect(on_node_removed)
    root = engine.load(MockItem, is_root=True)
    child_uuid = root.children[0].uuid
    engine.unload(root.children[0])
    assert on_node_removed.was_called


def test24_engine():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        foo = 123
        class MockChild(Item):
            @property
            def abc(scope):
                return scope.MockItem.foo
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert len(root.properties['foo'].dependents) == 1
    engine.unload(root.children[0])
    assert len(root.properties['foo'].dependents) == 0


def test25_engine():
    from pydeclarative.htmlwidgets import Item
    was_called = False
    class MockItem(Item):
        def handle_dom_event(scope, event):
            nonlocal was_called
            was_called = True
            assert event['event'] == 'native_event'
            assert event['event_name'] == 'clicked'
            assert event['uuid'] == get_node(scope).uuid
        
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    event = dict(event='native_event', event_name='clicked', uuid=root.uuid)
    engine.handle_dom_event(event, root)
    assert was_called


@pytest.mark.asyncio
async def test26_engine():
    engine = DeclarativeEngine()
    async def run_forever():
        await asyncio.Event().wait()
    engine.create_task(run_forever())
    assert len(engine.tasks) == 1
    engine.cancel_tasks()
    await asyncio.wait(engine.tasks)
    assert len(engine.tasks) == 0


def test27_engine():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    def on_custom_message(node, message_type, message):
        assert node.__eq__(root)
        assert message_type == 'foobar'
        assert message == dict(baf=1, baz=2, bar=3)
    engine.custom_message.connect(on_custom_message)
    engine.send_custom_message(root, 'foobar', dict(baf=1, baz=2, bar=3))


def test28_engine():
    engine = DeclarativeEngine()
    def on_custom_message(node, message_type, message):
        assert node is None
        assert message_type == 'bafbaz'
        assert message == dict(foo=1, bar=2, baz=3)
    engine.custom_message.connect(on_custom_message)
    engine.send_global_message('bafbaz', dict(foo=1, bar=2, baz=3))


def test29_engine():
    engine = DeclarativeEngine()
    def on_custom_message(node, message_type, message):
        assert node is None
        assert message_type == 'execute_js'
        assert message == dict(js='console.log("cowabanga!")')
    engine.custom_message.connect(on_custom_message)
    engine.execute_js('console.log("cowabanga!")')


def test30_property():
    class MockItem:
        @property
        def foobar(scope):
            return scope.foobar
    engine = DeclarativeEngine()
    node = Node(engine, MockItem, 'node')
    with pytest.raises(RuntimeError, match='Circular dependency'):
        node.init_members()


def test31_property():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        text = "foobar"
        @property
        def html(scope):
            return f'<input type="text" value="{scope.text}" />'
        @property
        def html_dup(scope):
            return scope.html
    def on_html_changed(node):
        on_html_changed.was_called = True
    on_html_changed.was_called = False
    engine = DeclarativeEngine()
    engine.html_changed.connect(on_html_changed)
    node = engine.load(MockItem, is_root=True)
    assert len(node.properties['html'].dependencies) == 1
    assert len(node.properties['html'].dependents) == 1
    assert len(node.properties['text'].dependents) == 1
    assert len(node.properties['html_dup'].dependencies) == 1
    assert not on_html_changed.was_called
    Scope(node).text = "barbaf"
    assert on_html_changed.was_called
    assert Scope(node).html_dup == '<input type="text" value="barbaf" />'


def test32_scope():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        class MockChild(Item):
            class MockGrandChild(Item):
                pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert isinstance(Scope(root).find_in_children('MockGrandChild'), Node)
    assert Scope(root).find_in_children('MockGrandChild') == root.children[0].children[0]


def test33_scope():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        class MockChild(Item):
            class MockGrandChildA(Item):
                pass
            class MockGrandChildB(Item):
                pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert root.children[0].children[0].id == 'MockGrandChildA'
    assert Scope(root.children[0].children[0]).find_in_parents('MockGrandChildB') == \
        root.children[0].children[1]
    assert Scope(root.children[0].children[1]).find_in_parents('MockGrandChildA') == \
        root.children[0].children[0]
    

def test34_scope():
    class MockItem:
        pass
    class MockEngine:
        pass
    mock_engine = MockEngine()
    node = Node(mock_engine, MockItem, 'node')
    with pytest.raises(ValueError, match='There is no parent'):
        _ = Scope(node).parent


def test35_scope():
    class MockItem:
        pass
    class MockEngine:
        pass
    mock_engine = MockEngine()
    node = Node(mock_engine, MockItem, 'node')
    with pytest.raises(AttributeError, match='not found'):
        _ = Scope(node).non_existent_property


def test36_scope():
    class MockItem:
        pass
    class MockEngine:
        pass
    mock_engine = MockEngine()
    node = Node(mock_engine, MockItem, 'node')
    assert isinstance(Scope(node).node, Node)


def test37_scope():
    class MockItem:
        pass
    class MockEngine:
        pass
    mock_engine = MockEngine()
    node = Node(mock_engine, MockItem, 'node')
    scope = Scope(node)
    orig_setattr = scope.__setattr__
    def mock_setattr(self, name, value):
        mock_setattr.was_called = True
        orig_setattr(name, value)
    mock_setattr.was_called = False
    scope.__dict__['__setattr__'] = partial(mock_setattr, scope)
    scope.node = None
    assert scope.node is None
    assert scope.__dict__['node'] is None
    assert not mock_setattr.was_called
    del scope.node
    # assert scope.node is None
    with pytest.raises(ValueError, match='no associated node'):
        _ = scope.node
    scope.__dict__['node'] = None
    assert scope.node is None


def test38_scope():
    class MockItem:
        pass
    class MockEngine:
        pass
    mock_engine = MockEngine()
    node = Node(mock_engine, MockItem, 'node')
    with pytest.raises(KeyError, match='not found'):
        _ = Scope(node)['non_existent_property']


def test39_scope():
    from pydeclarative.htmlwidgets import Item
    class MockItem(Item):
        class MockChild(Item):
            class MockGrandChild(Item):
                class MockGrandGrandChild(Item):
                    pass
    engine = DeclarativeEngine()
    root = engine.load(MockItem, is_root=True)
    assert Scope(root.children[0].children[0].children[0]).find_in_parents('MockItem') == root


def test40_scope():
    class MockItem:
        html = '<div />'
    class MockEngine:
        def __init__(self):
            self.html_changed = Signal()
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    node.init_members()
    node.is_loaded = True
    def on_html_changed(node):
        assert node.properties['html'].value == '<input type="text" placeholder="foobar" />'
        on_html_changed.was_called = True
    on_html_changed.was_called = False
    engine.html_changed.connect(on_html_changed)
    Scope(node).html = '<input type="text" placeholder="foobar" />'
    assert on_html_changed.was_called


def test41_scope():
    was_called = False
    class MockItem:
        foobar = '<div />'
        def on_foobar_changed(scope):
            nonlocal was_called
            was_called = True
    class MockEngine:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    node.init_members()
    node.is_loaded = True
    Scope(node).foobar = '<input type="text" placeholder="foobar" />'
    assert was_called


def test42_scope():
    was_called = False
    class MockItem:
        foobar = '<div />'
    class MockEngine:
        pass
    engine = MockEngine()
    node = Node(engine, MockItem, 'node')
    node.init_members()
    node.is_loaded = True
    Scope(node)['foobar'] = '<input type="text" placeholder="foobar" />'
    assert node.properties['foobar'].value == '<input type="text" placeholder="foobar" />'
