import logging.config
import re
from typing import Any
import yaml
import sys
import os
from datetime import datetime, timedelta
from inspect import stack
from enum import IntEnum


class Logger():
    # Constants - Logging levels
    class Level(IntEnum):
        DEBUG: int = logging.DEBUG
        CRITICAL: int = logging.CRITICAL
        ERROR: int = logging.ERROR
        INFO: int = logging.INFO
        WARNING: int = logging.WARNING

    # Types of log entry - different log types have slightly different formatted log payloads
    class LogEntryType(IntEnum):
        ENTRY: int = 1
        EXIT: int = 2
        PERF: int = 3
        STD: int = 0

    # Regexs to scan for and cleanse sensitive data in log messages
    SENSITIVE_DATA_PATTERN_LIST = {
        'email': r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})',
        'US_Social_Security_No': r'\b(?!000|666|9\d{2})([0-8]\d{2}|7([0-6]\d))([-]?|\s{1})(?!00)\d\d\2(?!0000)\d{4}\b',
        'IPV4_Address': r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)([ (\[]?(\.|dot)[ )\]]?(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})',
        'PC_MasterCard': r'^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$',
        "PC_VisaCard": r'\b([4]\d{3}[\s]\d{4}[\s]\d{4}[\s]\d{4}|[4]\d{3}[-]\d{4}[-]\d{4}[-]\d{4}|[4]\d{3}[.]\d{4}[.]\d{4}[.]\d{4}|[4]\d{3}\d{4}\d{4}\d{4})\b'
    }

    # Constants
    __LOGGING_CONFIG_DEFAULT = 'logger.yaml'

    # static variables
    __init = False

    # Lambda functions
    functionName = lambda: stack()[1][3]

    def LINE(back: int = 0) -> str:
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back += 1
        return str(sys._getframe(back + 1).f_lineno)

    def FILE(back: int = 0) -> str:
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back = back + 1
        return str(sys._getframe(back + 1).f_code.co_filename)

    def FUNC(back: int = 0) -> str:
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back = back + 1
        return str(sys._getframe(back + 1).f_code.co_name)

    def WHERE(back: int = 0) -> str:
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back = back + 1
        frame = sys._getframe(back + 1)
        return "%s/%s %s()" % (os.path.basename(frame.f_code.co_filename),
                               frame.f_lineno, frame.f_code.co_name)

    def ARGS(back: int = 0) -> str:
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back = back + 1
        frame = sys._getframe(back + 1)

        return str(frame.f_locals)

    def getLogger(name: str | None = '') -> logging.Logger:
        """Return a logger instance configured by the LOGGING_CONFIG_DEFAULT constant

        Parameters:
        name (str): the name of the logger

        Returns:
        Logger:Returning value

       """

        if (name is None):
            name = Logger.FUNC(1)

        if (Logger.__init is False):
            # Load the config file
            with open(Logger.__LOGGING_CONFIG_DEFAULT, 'rt') as f:
                config = yaml.safe_load(f.read())

            # Configure the logging module with the config file
            logging.config.dictConfig(config)

            Logger.__init = True

        return logging.getLogger(name)

    def entry(
              msg: str = '',
              *args,
              **kwargs):

        function_name: str = FUNC(1)
        Logger.getLogger(function_name).log(Logger.Level.DEBUG,
                                        Logger.logMsg(function_name, Logger.LogEntryType.ENTRY, '', None, '', msg, None, args,
                                                      kwargs))
        return

    def exit(func_name: str | None = '',
             duration: int | None = None,
             result: str | None = '',
             msg: str | None = '',
             *args,
             **kwargs):
        Logger.getLogger(func_name).log(Logger.Level.DEBUG,
                                        Logger.logMsg(func_name, Logger.LogEntryType.ENTRY, '', duration, result, msg, None,
                                                      args, kwargs))
        return

    def debug(func_name: str = '',
              duration: int | None = None,
              result: str = '',
              msg: str = '',
              *args,
              **kwargs):
        Logger.getLogger(func_name).log(Logger.Level.DEBUG,
                                        Logger.logMsg(func_name, Logger.LogEntryType.ENTRY, '', duration, result, msg, None,
                                                      args, kwargs))
        return

    def error(func_name: str = '',
              duration: int = None,
              result: str = '',
              msg: str = '',
              exception: Exception = None,
              *args,
              **kwargs):
        Logger.getLogger(func_name).log(Logger.Level.ERROR,
                                        Logger.logMsg(func_name, Logger.LogEntryType.STD, '', duration, result, msg, exception,
                                                      args,
                                                      kwargs))
        return

    def critical(func_name: str = '',
                 duration: int = None,
                 result: str = '',
                 msg: str = '',
                 exception: Exception = None,
                 *args,
                 **kwargs):
        Logger.getLogger(func_name).log(Logger.Level.CRITICAL,
                                        Logger.logMsg(func_name, Logger.LogEntryType.STD, '', duration, result, msg, exception,
                                                      args,
                                                      kwargs))
        return

    def logMsg(func_name: str | None = '',
               op_type: int = LogEntryType.STD,
               dec_msg: str | None = '',
               duration: int | None = None,
               result: str | None = '',
               msg: str | None = '',
               exception: Exception | None = None,
               *args: tuple[Any, ...] | None,
               **kwargs: dict[str, Any] | None) -> str:
        """Return a correctly formatted log message

        Parameters:
        func_name (str): the function name the log entry is assigned
        op_type (int): class LogEntryType - ENTRY|EXIT|PERF|STD
        dec_msg (str): function decorator message - see @logMe
        duration (int): a duration value (eg the time interval between exit and entry log entries
        result (str): a function return value
        msg (str): the general message to log
        exception (Exception): an exception value which needs to be logged
        *args (str[]): additional args
        **kwargs (str[]): addition name/value pair args

        Returns:
        result (str): standard log msg correctly formatted

       """
        argsStr = ''
        if (args is None or args.__sizeof__() == 0):
            args_str = Logger.ARGS(1)
        else:
            args_str = args.__str__()

        kwargsStr = ''
        if (kwargs is None or kwargs.__sizeof__() == 0):
            kwargs_str = ''
        else:
            kwargs_str = kwargs.__str__()

        # Add exception details to the main log message
        exception_str = ''
        if (exception is not None):
            exception_str = exception.__str__()

        if (dec_msg is not None):
            dec_msg = dec_msg.replace('|', ',')

        if (msg is not None):
            msg = msg.replace('|', ',')

        prefix: str = '|'.join([Logger.FILE(1), Logger.LINE(1), Logger.FUNC(1)])

        if op_type == Logger.LogEntryType.ENTRY:
            result: str = f'{prefix}|{func_name}|Enter|{dec_msg}||||{msg}|{args_str}|{kwargs_str}||{exception_str}'
        elif op_type == Logger.LogEntryType.EXIT:
            result: str = f'{prefix}|{func_name}|Exit||{dec_msg}|{duration}|{result}|{msg}||||{exception_str}'
        else:
            result: str = f'{prefix}|{func_name}|-|||||{msg}||||{exception_str}'

        # clean data in log entry
        for key, regex in Logger.SENSITIVE_DATA_PATTERN_LIST.items():
            result = re.sub(regex, '****', result)

        return result


def logMe(level: int = logging.DEBUG, enter_msg: str | None = '', exit_msg: str | None = ''):
    """ Decorator to add log entry and exit log entries for the function. Also any exception thrown will be logged and rethrown

    Parameters:
    level (int): class Level - DEBUG|CRITICAL|ERROR|INFO|WARNING
    enter_msg (str): added to the function entry log entry
    exit_msg (str): added to the function exit log entry

    Returns:
    decorator: Returning value

   """

    def decorator(fun):
        func_name: str = fun.__name__

        def wrapper(*args, **kwargs):
            result = None
            start: datetime = datetime.now()
            try:
                Logger.getLogger(__name__).log(level,
                                               Logger.logMsg(func_name, Logger.LogEntryType.ENTRY, enter_msg, None, None, None,
                                                             None, args,
                                                             kwargs))
                result = fun(*args, **kwargs)
            except Exception as e:
                finish: datetime = datetime.now()
                exe_duration: timedelta = finish - start

                Logger.getLogger(__name__).log(logging.ERROR,
                                               Logger.logMsg(func_name, Logger.LogEntryType.STD, exit_msg,
                                                             int(exe_duration.total_seconds()),
                                                             result, None, e, None, None))
                raise
            finally:
                finish: datetime = datetime.now()
                exe_duration: timedelta = finish - start
                Logger.getLogger(__name__).log(level,
                                               Logger.logMsg(func_name, Logger.LogEntryType.EXIT, exit_msg,
                                                             int(exe_duration.total_seconds()), result, None, None,
                                                             None, None))

            return result

        return wrapper

    return decorator


"""
# TODOs
1. Add functions to create standard formatted log entries for the different type : entry , exit etc
2. filter for and clean sensitive data
"""
