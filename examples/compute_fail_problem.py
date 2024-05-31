from pydeclarative import *


class root(Div):
    class numberOne(TextInput):
        text = '5'

    class numberTwo(TextInput):
        text = '9'

    class _changeBindingBtn(Button):
        text = "Change binding"
        def on_clicked(scope):
            scope.changeBinding.text = Binding(lambda scope: str(float(scope.numberOne.text) * float(scope.numberTwo.text)))

    class changeBinding(TextOutput):
        @property
        def text(scope):
            return str(float(scope.numberOne.text) + float(scope.numberTwo.text))
