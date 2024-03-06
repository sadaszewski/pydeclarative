from pydeclarative import *

class root(Div):
    class userName(TextInput):
        placeholder = "Enter your name here"

    class _p(Paragraph):
        def innerText(scope):
            return f"Hello {scope['userName'].get_value()}"


def main():
    engine = DeclarativeEngine()
    engine.load(root)


if __name__ == '__main__':
    main()
