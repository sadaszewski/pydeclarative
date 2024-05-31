from pydeclarative import *


def print_properties(title, props):
    print(title)
    for p in props:
        print(repr(p) + ' in node: ' + repr(p.node.real_self) + ' dependencies:' + ', '.join(repr(p_1) for p_1 in p.dependencies))


class root(Item):
    display_number = "a"

    class aNumber(TextInput):
        placeholder = "Type number A here"

    class bNumber(TextInput):
        placeholder = "Type number B here"

    class _info(TextOutput):
        @property
        def text(scope):
            return f'Displaying number: {scope.parent.display_number}'

    class mirror(TextOutput):
        text = LazyBinding(lambda scope: scope.root.binding_a)

    def binding_a(scope):
        return scope.aNumber.text

    def binding_b(scope):
        return scope.bNumber.text

    class _btn(Button):
        text = "Click me"
        def on_clicked(scope):
            if scope.parent.display_number == 'a':
                scope.parent.display_number = 'b'
                scope.mirror.text = Binding(scope.root.binding_b)
            else:
                scope.parent.display_number = 'a'
                scope.mirror.text = Binding(scope.root.binding_a)
            print_properties('mirror dependencies:', get_node(scope.mirror).properties['text'].dependencies)
            print_properties('aNumber dependents:', get_node(scope.aNumber).properties['text'].dependents)
            print_properties('bNumber dependents:', get_node(scope.bNumber).properties['text'].dependents)