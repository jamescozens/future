from util import logger

"""""
logger.getLogger(__name__).debug('This is a debug message')
logger.getLogger(__name__).info('This is an info message')
logger.getLogger(__name__).warning('This is a warning message')
logger.getLogger(__name__).error('This is an error message')
logger.getLogger(__name__).critical('This is a critical message')
"""""


@logger.logMe(logger.Level.DEBUG, "333333", "444444")
def stringJoin(*args):
    st = ''
    for i in args:
        st += i
    logger.getLogger(__name__).debug(f"{logger.functionName()}|st={st}")
    return st


@logger.logMe(logger.Level.DEBUG, "333|||||||||||||||333", "{|x}")
def raiseException(*args):
    x = 20 / 0
    return None


@logger.logMe()
def test(*args):
    x = 20 / 1
    return None


test()
stringJoin("aaaa", "bbbbb", "ccc", "dddddd", "eeeeeee")
raiseException()
