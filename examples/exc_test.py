from pydeclarative import *


class root(Item):
    class _textInput(TextInput):
        placeholder = 'Type here to cause an exception'
        def on_text_changed(scope):
            raise RuntimeError('Exception in on_text_changed()')

    class _btn(Button):
        text = 'Click me to cause an exception'
        def on_clicked(scope):
            raise RuntimeError('Exception in on_clicked()')
        
    class timer(Timer):
        running = False
        def on_triggered(scope):
            raise RuntimeError('Exception in on_triggered()')
        
    class _btn1(Button):
        @property
        def text(scope):
            return ("Start timer" if not scope.timer.running else "Stop timer")
        def on_clicked(scope):
            scope.timer.running = not scope.timer.running
        
    def on_loaded(scope):
        raise RuntimeError('Exception in on_loaded()')
    
    def on_unloaded(scope):
        raise RuntimeError('Exception in on_unloaded()')
