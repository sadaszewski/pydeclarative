from pydeclarative import *
from pydeclarative.signal import Signal


class root(Item):
    x = 1
    foobared = Signal()
    class _btn(Button):
        text = 'Click me!'
        def on_clicked(scope):
            scope.root.x += 1
    class _btn2(Button):
        text = 'Unload inner'
        def on_clicked(scope):
            get_engine(scope).unload(get_node(scope._inner))
    class _btn3(Button):
        text = 'Foobar me'
        def on_clicked(scope):
            scope.root.foobared()
    class _inner(Item):
        class _deeper(Item):
            class _conn(Connections):
                target = Binding(lambda scope: scope.root)
                def on_x_changed(scope):
                    print('x is now:', scope.root.x)
                def on_foobared(scope):
                    print('I got foobared')
