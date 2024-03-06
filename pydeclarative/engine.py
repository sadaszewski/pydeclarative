import inspect
from .htmlwidgets import Item

class Instance:
    def __init__(self):
        pass


class DeclarativeEngine:
    def __init__(self):
        pass

    def load(self, item):
        children = [ (k, v, v.__base__) for k, v in item.__dict__.items() if inspect.isclass(v) and issubclass(v, Item) ]
        print('children:', children)
