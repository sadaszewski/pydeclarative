from pydeclarative import *


class Baf(TabPane):
    css_class = [ 'p-3' ]
    class _textOutput(TextOutput):
        text = 'baf'
    class _btn(Button):
        text = "Click me!"
        def on_clicked(scope):
            scope.popupDialog.open()
    class _btn1(Button):
        text = "Change color of 1st tab"
        def on_clicked(scope):
            scope._foo.css_style = { 'background-color': 'red' }


class root(Item):
    class _pills(NavPills):
        css_class = [ 'm-3' ]
        tab_names = [ 'foo', 'bar', 'baf' ]
        class _foo(TabPane):
            first = True
            css_class = [ 'p-3' ]
            css_style = {}
            class _textOutput(TextOutput):
                text = 'foo'
        class _bar(TabPane):
            css_class = [ 'p-3' ]
            class _textOutput(TextOutput):
                text = 'bar'
        class _baf(Baf):
            pass
        
    class popupDialog(StandardModal):
        title = "Popup Dialog"
        message = "Hello, NavPills!"