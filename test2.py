import os
import sys
import time

from pack2.green.spades import test as spade_test
from util.logger import Logger, logMe


def testXYZQQQQ(a: str, b: int):
    log_context = Logger.entry('entry into testXYZQQQQ')

    log_context = Logger.debug('about to call function in module pack2.green.spades', context=log_context)

    spade_test('454354535', '457437vbii vosifbvsdugfhodsi8ub s00usyb gdofsuhofgsd8b ')

    i=32/0

    Logger.exit('exit from testXYZQQQQ', context=log_context)
    return


if __name__ == "__main__":
    Logger._log_stack_depth=True
    log_context = Logger.entry( f'main start - {sys.argv}', )
    try:
        log_context = Logger.debug('about to call testXYZQQQQ', context=log_context)
        result = testXYZQQQQ('PPPPPP', 8887654)
        log_context = Logger.info('done with testXYZQQQQ', result=result, context=log_context)
    except Exception as e:
        log_context = Logger.error('finished calling testXYZQQQQ', None, None, e, context=log_context)
    finally:
        log_context = Logger.info('about to leave testXYZQQQQ - do not worry about any exceptions thrown by it', context=log_context)

    Logger.exit('main exit', context=log_context)