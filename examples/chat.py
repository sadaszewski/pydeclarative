from pydeclarative import *
from pydeclarative.signal import Signal


class GlobalState:
    def __init__(self):
        self.message_received = Signal()

    def send_message(self, nickname, message):
        print('!!! message_received.connections:', self.message_received.connections)
        self.message_received(nickname, message)

    def __copy__(self):
        return self

    def __deepcopy__(self):
        return self


global_state = GlobalState()


class root(Item):
    has_joined = False
    message_received_conn = None
    class nickname(TextInput):
        placeholder = 'Type your nickname here'
        @property
        def disabled(scope):
            return scope.parent.has_joined
    class _joinBtn(Button):
        text = "Join the chat"
        @property
        def disabled(scope):
            return scope.parent.has_joined
        def on_clicked(scope):
            if scope.nickname.text == '':
                scope.nickname.text = 'Anonymous'
            scope.parent.has_joined = True
    class _joinInfo(TextOutput):
        text = 'You have joined the chat'
        @property
        def css_style(scope):
            return dict(display='none') if not scope.parent.has_joined else dict()
    class _div(Div):
        css_style = { 'display': 'grid', 'grid-auto-flow': 'column' }
        class messageEditor(TextInput):
            placeholder = 'Type your message here'
            @property
            def disabled(scope):
                return not scope.root.has_joined
        class _messageLengthDisplay(TextOutput):
            @property
            def text(scope):
                return str(len(scope.messageEditor.text))
        class _sendBtn(Button):
            text = "Send"
            @property
            def disabled(scope):
                return not scope.root.has_joined
            def on_clicked(scope):
                global_state.send_message(scope.nickname.text, scope.messageEditor.text)
                scope.messageEditor.text = ''
    class messages(Repeater):
        model = ListModel()
        @delegate
        class delegate(Div):
            index = None
            model_data = None
            class _textOutput(TextOutput):
                @property
                def text(scope):
                    return f'{scope.parent.model_data[0]} says: {scope.parent.model_data[1]}'
    def on_loaded(scope):
        print('!!! on_loaded()')
        scope.message_received_conn = global_state.message_received.connect(scope.message_received_callback)
    def on_unloaded(scope):
        print('disconnecting message_received_conn')
        global_state.message_received.disconnect(scope.message_received_conn)
    def message_received_callback(scope, nickname, message):
        print('!!! message_received_callback()', nickname, message)
        scope.messages.model.append(( nickname, message ))
