import logging
import os

from util.logger import Logger, logMe


def test(xyz, qwe):
    log_context = Logger.entry('enter spades.test()')

    try:
        a2('eeeeee', param2='tttttt')
    except:
        Logger.warning('call to a2() raised an error, but we are carrying on!', context=log_context)
    finally:
        Logger.info('post call to a2() all good', context=log_context)

    Logger.debug('post call to a2() and do something...', context=log_context)

    Logger.entry('exist spades.test()', context=log_context)
    return


# @logMe(log_package = __package__)
@logMe(level=logging.CRITICAL, enter_msg='going in... to function', exit_msg='leaving func....')
def a2(param1, param2, param3 = '242342'):
    Logger.debug('inside a2() and about to return... (no context to share)')
    z = 10 / 1
    return 'a2 result'

