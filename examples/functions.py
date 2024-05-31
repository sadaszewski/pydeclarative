from pydeclarative import Div, \
    DeclarativeEngine, \
    Node, \
    Scope


class root(Div):
    a = 2
    b = 3
    name = 'world'

    def msg(scope):
        return f'Hello, {scope.name}!'

    @property
    def c(scope):
        return scope.complex_expression(scope.a, scope.b)

    def complex_expression(scope, x, y):
        return x ** 2 + y ** 3

    def hello_world(scope):
        print(scope.msg())


def main():
    engine = DeclarativeEngine()
    node = Node(engine, root, 'root', None)
    node.init_members()
    scope = Scope(node)
    scope.hello_world()
    print('c:', scope.c)
    scope.b = 4
    print('c:', scope.c)
    scope.name = 'foobar'
    scope.hello_world()
    # print(node.functions)


if __name__ == '__main__':
    main()
