from pydeclarative import *
from pydeclarative.signal import Signal
import gc
import logging
import sys


class GlobalState:
    signal = Signal()


class root(Item):
    def on_loaded(scope):
        print('on_loaded()')
        GlobalState.signal.connect(scope.dummy_callback)
    def dummy_callback(scope):
        print('dummy_callback()')


def dummy():
    return Node(None, None, 'x')



def fun1():
    logger = logging.getLogger()
    engine = DeclarativeEngine()
    logger.info(f'# refs to engine: {sys.getrefcount(engine)}')
    # node = dummy() # engine.load(root, is_root=True)
    node = Node(None, None, 'x')
    logger.info(f'# refs to engine: {sys.getrefcount(engine)}')
    # gc.collect()
    logger.info(f'# refs to node: {sys.getrefcount(node)}')
    logger.info(gc.get_referrers(node))
    logger.info(f'# refs to node: {sys.getrefcount(node)}')
    #logger.info(locals())
    #logger.info(globals())


def fun2():
    logger = logging.getLogger()
    from examples.chat import root, global_state
    engine = DeclarativeEngine()
    node = engine.load(root, is_root=True)
    print(global_state.message_received.connections)
    logger.info(f'# refs to node: {sys.getrefcount(node)}')
    return global_state

def main1():
    logger = logging.getLogger()
    node = Node(None, None, 'x')
    logger.info(f'! # refs to node: {sys.getrefcount(node)}')
    fun2()
    fun2()
    from examples.chat import global_state
    logger.info(global_state.message_received.connections)
    logger.info('here')

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    main1()
    logger.info('HERE')


if __name__ == '__main__':
    main()
