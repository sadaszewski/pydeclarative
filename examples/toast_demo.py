from pydeclarative import *


class root(Item):
    class _btn(Button):
        css_class = [ 'm-3' ]
        text = "Click me"
        def on_clicked(scope):
            scope.toastContainer.add_toast("Toast title", "Hello, world!", autohide=False, color="success")
    class toastContainer(ToastContainer):
        pass
