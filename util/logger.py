import logging.config
import re
import yaml
from logging import Logger
from datetime import datetime, timedelta
from inspect import stack
from enum import IntEnum

# Constants - Logging levels
class Level(IntEnum):
    DEBUG: int = logging.DEBUG
    CRITICAL: int = logging.CRITICAL
    ERROR: int = logging.ERROR
    INFO: int = logging.INFO
    WARNING: int = logging.WARNING


class LogEntryType(IntEnum):
    ENTRY: int = 1
    EXIT: int = 2
    PERF: int = 3
    STD: int = 0

# Constants
LOGGING_CONFIG_DEFAULT = 'logger.yaml'

# Regexs to scan for and cleanse sensitive data in log messages
_sensitiveDataPattern = {
    'email' : r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})',
    'US_Social_Security_No' : r'\b(?!000|666|9\d{2})([0-8]\d{2}|7([0-6]\d))([-]?|\s{1})(?!00)\d\d\2(?!0000)\d{4}\b',
    'IPV4_Address' : r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)([ (\[]?(\.|dot)[ )\]]?(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})',
    'PC_MasterCard': r'^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$',
    "PC_VisaCard": r'\b([4]\d{3}[\s]\d{4}[\s]\d{4}[\s]\d{4}|[4]\d{3}[-]\d{4}[-]\d{4}[-]\d{4}|[4]\d{3}[.]\d{4}[.]\d{4}[.]\d{4}|[4]\d{3}\d{4}\d{4}\d{4})\b'
}

# Private package variables
__init = False

# Lambda functions
functionName = lambda: stack()[1][3]


def getLogger(name: str) -> Logger:
    if (name is None):
        name = "__main__"

    global __init
    if (__init is False):
        # Load the config file
        with open(LOGGING_CONFIG_DEFAULT, 'rt') as f:
            config = yaml.safe_load(f.read())

        # Configure the logging module with the config file
        logging.config.dictConfig(config)

        __init = True

    return logging.getLogger(name)


def logMe(level: int=logging.DEBUG, enter_msg: str="", exit_msg: str=""):
    def decorator(fun):
        func_name : str = fun.__name__
        def wrapper(*args, **kwargs):
            result = None
            start: datetime = datetime.now()
            try:
                getLogger(__name__).log(level,
                                        logMsg(func_name, LogEntryType.ENTRY, enter_msg, None, None, None, None, args, kwargs))
                result = fun(*args, **kwargs)
            except Exception as e:
                finish: datetime = datetime.now()
                exe_duration: timedelta = finish - start

                getLogger(__name__).log(logging.ERROR,
                                        logMsg(func_name, LogEntryType.STD, exit_msg, int(exe_duration.total_seconds()), result, None, e, None, None))
                raise
            finally:
                finish: datetime = datetime.now()
                exe_duration: timedelta = finish - start
                getLogger(__name__).log(level,
                                        logMsg(func_name, LogEntryType.EXIT, exit_msg, int(exe_duration.total_seconds()), result, None, None, None, None))

            return result
        return wrapper
    return decorator

def logMsg(func_name: str = '',
           op_type: LogEntryType = LogEntryType.STD,
           dec_msg: str = '',
           duration: int = None,
           result: str = '',
           msg: str = '',
           exception : Exception = None,
           *args,
           **kwargs) -> str:

    argsStr = ''
    if (args is None or  args.__sizeof__() == 0):
        args_str = ''
    else:
        args_str = args.__str__()

    kwargsStr = ''
    if (kwargs is None or kwargs.__sizeof__() == 0):
        kwargs_str = ''
    else:
        kwargs_str = kwargs.__str__()

    # Add exception details to the main log message
    exception_str=''
    if (exception is not None):
        exception_str = exception.__str__()

    if (dec_msg is not None):
        dec_msg = dec_msg.replace('|',',')

    if (msg is not None):
        msg = msg.replace('|', ',')

    if op_type == LogEntryType.ENTRY:
        result: str = f'{func_name}|Enter|{dec_msg}||||{msg}|{args_str}|{kwargs_str}||{exception_str}'
    elif op_type == LogEntryType.EXIT:
        result: str = f'{func_name}|Exit||{dec_msg}|{duration}|{result}|{msg}||||{exception_str}'
    else:
        result: str = f'{func_name}|-|||||{msg}||||{exception_str}'

    for key, regex in _sensitiveDataPattern.items():
      result = re.sub(regex, '****', result)

    return result


"""
# TODOs
1. Add functions to create standard formatted log entries for the different type : entry , exit etc
2. filter for and clean sensitive data
"""
print(logMsg('aaaaa', LogEntryType.ENTRY,'dec enter',999, 'dfdfs' , '4111111111111111 sadgsdgjd  jim@dfdsf.com sddfsdfsd 121.34.121.123',None, None, None))

