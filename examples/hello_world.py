from pydeclarative import *
import PIL.Image
import random
import pdb


red_image = PIL.Image.new('RGB', (128, 128), 'red')


class MyButton(Button):
    css_class = 'btn-lg'
    css_style = 'color: red;'
    is_outline_button = True


class MyDiv(Div):
    css_style = 'width: 128px; height: 128px; background: green; margin: 5px;'


class root(Div):
    counter = 0
    dynamic_nodes = []

    class username(TextInput):
        placeholder = "Enter your name here"
        def on_loaded(scope):
            print('username loaded')

    class _message(TextOutput):
        @property
        def text(scope):
            return f"Hello, {scope.username.text}!"
        def on_loaded(scope):
            print('_message loaded')

    class _btn(MyButton):
        def on_clicked(scope):
            print('Clicked')
            scope.root.counter += 1
        def on_loaded(scope):
            print('_btn loaded')

    class _btn1(MyButton):
        text = "Add item"
        def on_clicked(scope):
            node = get_engine(scope).load(MyDiv, is_root=True, parent=scope.root)
            scope.root.dynamic_nodes.append(node)

    class _btn2(MyButton):
        text = "Remove item"
        def on_clicked(scope):
            if scope.root.dynamic_nodes:
                get_engine(scope).unload(scope.root.dynamic_nodes.pop())

    class _clickCounter(TextOutput):
        @property
        def text(scope):
            return f'You have clicked the button: {scope.root.counter} times.'
        def on_loaded(scope):
            print('_clickCounter loaded')

    class _img(Image):
        source = red_image

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
        @property
        def text(scope):
            return ('Stop timer' if scope.timer.running else 'Start timer')
        def on_clicked(scope):
            # pdb.set_trace()
            scope.timer.running = not scope.timer.running

    class terminal(Terminal):
        pass

    class _addLineToTerminal(Button):
        text = "Add line"
        def on_clicked(scope):
            get_engine(scope).send_custom_message(scope.terminal, 'append', dict(text='foobar\n'))

    class repeater(Repeater):
        @delegate
        class delegate(TextOutput):
            index = None
            model_data = None
            @property
            def text(scope):
                return f'Index: {scope.index}, model_data: {scope.model_data}'

        model = ListModel([ 'foo', 'bar', 'baf', 'baz' ])

    class _modelAppendBtn(Button):
        text = "Append item to model"
        def on_clicked(scope):
            scope.repeater.model.append('foo%03d' % random.randint(0, 100))

    class _modelInsertBtn(Button):
        text = "Insert item to model"
        def on_clicked(scope):
            pos = random.randint(0, len(scope.repeater.model))
            print('pos:', pos)
            scope.repeater.model.insert(pos,
                'foo%03d' % random.randint(0, 100))

    class _modelRemoveBtn(Button):
        text = "Remove item"
        def on_clicked(scope):
            pos = random.randint(0, len(scope.repeater.model) - 1)
            print('pos:', pos)
            scope.repeater.model.remove(pos)

    class _div(Div):
        pass

    class _executeJsBtn(Button):
        @property
        def text(scope):
            return 'Enable buttons (execute JS)' if scope.buttons_disabled else 'Disable buttons (execute JS)'
        buttons_disabled = False
        def on_clicked(scope):
            print('execute js button clicked')
            scope.buttons_disabled = not scope.buttons_disabled
            if scope.buttons_disabled:
                get_engine(scope).execute_js('''$('button').attr('disabled', 'disabled'); $('#''' + get_node(scope).uuid + '''').attr('disabled', null)''')
            else:
                get_engine(scope).execute_js('''$('button').attr('disabled', null)''')

    class _gridRepeater(Repeater):
        model = ListModel('lorem ipsum dolor sit amet adpiscin elit stabat mater dolorosa ius gentum ad coelum'.split())
        @delegate
        class delegate(Div):
            index = None
            model_data = None
            css_class = ['card', 'm-2', 'float-start']
            css_style = dict(width='18rem')
            class _text(TextOutput):
                css_class = 'card-body'
                @property
                def text(scope):
                    return scope.delegate.model_data
        css_class = 'clearfix'
        css_style = {
            #'display': 'grid',
            #'grid-auto-flow': 'dense'
        }

    class _failBtn(Button):
        text = "I will fail"
        def on_clicked(scope):
            x = foo // bar

    class _div2(Div):
        pass

    class numberOne(TextInput):
        text = '5'

    class mathOp(TextOutput):
        text = '+'

    class numberTwo(TextInput):
        text = '9'

    def binding_sum(scope):
        return str(float(scope.numberOne.text) + float(scope.numberTwo.text))

    def binding_mul(scope):
        return str(float(scope.numberOne.text) * float(scope.numberTwo.text))

    class _changeBindingBtn(Button):
        text = "Change binding"
        def on_clicked(scope):
            if scope.mathOp.text == '+':
                scope.mathOp.text = '*'
                scope.changeBinding.text = Binding(scope.root.binding_mul)
            else:
                scope.mathOp.text = '+'
                scope.changeBinding.text = Binding(scope.root.binding_sum)

    class changeBinding(TextOutput):
        @property
        def text(scope):
            return scope.root.binding_sum()

    def on_loaded(scope):
        print('root loaded')


def main():
    engine = DeclarativeEngine()
    engine.load(root, inflate=True)


if __name__ == '__main__':
    main()
