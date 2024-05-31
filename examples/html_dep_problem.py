from pydeclarative import *
import pdb


class root(Div):
    class timer(Timer):
        count = 0
        running = False

        def on_triggered(scope):
            print('my timer triggered')
            scope.count += 1

    class _timerCounter(TextOutput):
        @property
        def text(scope):
            return f'The timer was triggered: {scope.timer.count} times'

    class _startStopTimerBtn(Button):
        text = 'Start timer'
        def on_clicked(scope):
            # pdb.set_trace()
            scope.timer.running = not scope.timer.running
            scope.text = 'Stop timer' if scope.timer.running else 'Start timer'

    class _dummyButton(Button):
        text = "Click me"
