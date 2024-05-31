from pydeclarative import Node, \
    Property, \
    Div, \
    DeclarativeEngine, \
    Scope


class root(Div):
    a = 1
    e = 7
    def b(scope):
        return scope['a'] * 2 + scope.get('c', 0) * 3
    def c(scope):
        return scope['a'] / 5 + scope['e']
    def d(scope):
        return f'Hello a: {scope["a"]}, b: {scope["b"]}, c: {scope["c"]}!'


def main():
    engine = DeclarativeEngine()
    node = Node(engine, root, 'root', None)
    node.init_static_properties()
    node.init_dynamic_properties()
    print(node.properties)
    scope = Scope(node)
    print('a:', scope['a'], 'b:', scope['b'], 'c:', scope['c'], 'd:', scope['d'])
    scope['a'] = 3
    print('a:', scope['a'], 'b:', scope['b'], 'c:', scope['c'], 'd:', scope['d'])
    print(node.properties)


if __name__ == '__main__':
    main()
