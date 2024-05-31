from pydeclarative import Node, \
    Property, \
    Div, \
    DeclarativeEngine, \
    Scope


class root(Div):
    a = 1
    def b(scope):
        return scope['a'] * 2
    def c(scope):
        return scope['b'] * 2
    def d(scope):
        return scope['e']
    def e(scope):
        return scope['d']
    name = 'Foo'
    def hello(scope):
        return f'Hello, {scope["name"]}, {scope["b"]}, {scope["c"]}, {scope["d"]}!'


def main():
    engine = DeclarativeEngine()
    node = Node(engine, root, 'root', None)
    node.init_static_properties()
    node.init_dynamic_properties()
    print(node.properties)
    scope = Scope(node)
    print('a:', scope['a'], 'b:', scope['b'], 'c:', scope['c'], 'd:', scope['d'], 'e:', scope['e'])
    scope['a'] = 3
    print('a:', scope['a'], 'b:', scope['b'], 'c:', scope['c'], 'd:', scope['d'], 'e:', scope['e'])
    scope['d'] = 1
    print('a:', scope['a'], 'b:', scope['b'], 'c:', scope['c'], 'd:', scope['d'], 'e:', scope['e'])
    scope['e'] = 2
    print('a:', scope['a'], 'b:', scope['b'], 'c:', scope['c'], 'd:', scope['d'], 'e:', scope['e'])
    print('name:', scope['name'], 'hello:', scope['hello'])
    scope['name'] = 'Shiloh'
    print('name:', scope['name'], 'hello:', scope['hello'])
    print(node.properties)


if __name__ == '__main__':
    main()
