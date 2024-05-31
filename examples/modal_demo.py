from pydeclarative import *


class root(Item):
    class _btn(Button):
        text = "Click me"
        def on_clicked(scope):
            scope.popupDialog.open()
    class _btn1(Button):
        text = "Message box"
        def on_clicked(scope):
            scope.messageBox.show("Message box", "Just a friendly message box.", accept_button_text="KK")
    class popupDialog(StandardModal):
        title = "Modal Dialog Demo"
        def on_accepted(scope):
            get_engine(scope).execute_js('''console.log("accepted")''')
        def on_rejected(scope):
            get_engine(scope).execute_js('''console.log("rejected")''')
        class _body(ModalBody):
            class _textOutput(HTMLOutput):
                content = '''<span style="color: red;">Custom body is possible</span>'''
            class _textInput(TextInput):
                placeholder = 'Lorem ipsum dolor sit amet'
    class messageBox(MessageBox):
        pass