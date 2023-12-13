import inspect
import logging.config
import re
import time
from itertools import count
from typing import Any
import yaml
import sys
import os
from datetime import datetime, timedelta
from inspect import stack
from enum import IntEnum


class Logger:
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

    class LogContext:
        def __init__(self):
            self._start_time = Logger.LogContext.getPerfTime()

        @property
        def start_time(self):
            return self._start_time

        @start_time.setter
        def start_time(self, value):
            self._start_time = value

        @start_time.deleter
        def start_time(self):
            del self._start_time

        def getPerfTime() -> int:  # static function
            return time.clock_gettime_ns(0)

    # Regexs to scan for and cleanse sensitive data in log messages
    SENSITIVE_DATA_PATTERN_LIST = {
        'email': r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})',
        'US_Social_Security_No': r'\b(?!000|666|9\d{2})([0-8]\d{2}|7([0-6]\d))([-]?|\s{1})(?!00)\d\d\2(?!0000)\d{4}\b',
        'IPV4_Address': r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)([ (\[]?(\.|dot)[ )\]]?(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})',
        'PC_MasterCard': r'^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$',
        "PC_VisaCard": r'\b([4]\d{3}[\s]\d{4}[\s]\d{4}[\s]\d{4}|[4]\d{3}[-]\d{4}[-]\d{4}[-]\d{4}|[4]\d{3}[.]\d{4}[.]\d{4}[.]\d{4}|[4]\d{3}\d{4}\d{4}\d{4})\b'
    }

    # Constants
    __LOGGING_CONFIG_DEFAULT: str = 'logger.yaml'
    __HOME_PATH: str = os.path.abspath(__file__)[0:os.path.abspath(__file__).rfind(f'{os.sep}{__package__}')]

    # Static Variables
    __init: bool = False
    _log_stack_depth: bool = False

    # Lambda functions
    functionName = lambda: stack()[1][3]

    def LINE(back: int = 0) -> int:
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back += 1
        return sys._getframe(back + 1).f_lineno

    def MOD(back: int = 0) -> str:
        result: str | None = ''
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back += 1

        frame = sys._getframe(back + 1)
        result = inspect.getmodulename(frame.f_code.co_filename)
        #        result = frame.f_globals['__name__']

        return result

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

    def LOCAL_VARS(back: int = 0) -> str:
        if (str(sys._getframe(back + 1).f_code.co_name) == 'wrapper'):
            back = back + 1
        frame = sys._getframe(back + 1)

        # return str(inspect.getargvalues(frame))
        return str(frame.f_locals)

    def QUALIFIED_MOD(mod_path: str | None = None, os_file_sep: str = os.path.sep) -> str | None:
        result: str | None = None

        # Logger.__HOME_PATH = /Users/jamecoze/PycharmProjects/future
        # mod_path = /Users/jamecoze/PycharmProjects/future/pack2/green/spades.py

        if (mod_path is None or mod_path == ''):
            return None

        if (len(mod_path) < 3):
            return mod_path
        else:
            mod_path = mod_path[0:len(mod_path) - 3]  # strip out the end '.py' characters

        if (len(Logger.__HOME_PATH) < 1):
            return mod_path

        if (len(mod_path) < len(
                Logger.__HOME_PATH)):  # this should not happen, guard against corrupt/invalid mod_path value
            return mod_path

        if (Logger.__HOME_PATH is None or Logger.__HOME_PATH == ''):  # the home dir is not defined
            return mod_path

        module_only_path: str = mod_path[len(Logger.__HOME_PATH) + 1:len(mod_path)]

        if (module_only_path is not None):
            result = module_only_path.replace(os_file_sep, '.')  # replace the dir delimiters with '.' characters

        return result

    def STACK_DEPTH(back: int = 0):
        frame = sys._getframe(back + 1)

        for size in count(back):
            frame = frame.f_back
            if not frame:
                return size



    def getLogger(name: str | None = None) -> logging.Logger:
        """Return a logger instance configured by the LOGGING_CONFIG_DEFAULT constant

        Parameters:
        name (str): the name of the logger

        Returns:
        Logger:Returning value

       """

        logger_name = 'root'
        if (name is not None and name != ''):
            logger_name = name

        if (Logger.__init is False):
            # Load the config file
            with open(Logger.__LOGGING_CONFIG_DEFAULT, 'rt') as f:
                config = yaml.safe_load(f.read())

            # Configure the logging module with the config file
            logging.config.dictConfig(config)

            Logger.__init = True

        return logging.getLogger(logger_name)

    def entry(msg: str | None = '',
              *,
              context: LogContext | None = None) -> LogContext:
        module: str | None = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

        stack_depth: int = 0
        if Logger._log_stack_depth == True:
            stack_depth = Logger.STACK_DEPTH(1)


        logger_name: str | None = None
        if (module is None or module == '' or module.find('.') < 0):
            logger_name = 'root'  # Logger.MOD(1) |   __package__
        else:
            logger_name = module[0:module.rfind('.')]

        Logger.getLogger(logger_name).log(Logger.Level.DEBUG,
                                          Logger.logMsg(module, Logger.FUNC(1), Logger.LINE(1),
                                                        Logger.LogEntryType.ENTRY, 0, None,
                                                        msg, None,
                                                        Logger.LOCAL_VARS(1), stack_depth))

        if context is None:
            context = Logger.LogContext()

        return context

    def exit(msg: str | None = '',
             duration: int | None = None,
             result: Any | None = None,
             *,
             context: LogContext | None = None) -> LogContext:
        module: str | None = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

        stack_depth: int = 0
        if Logger._log_stack_depth == True:
            stack_depth = Logger.STACK_DEPTH(1)

        logger_name: str | None = None
        if (module is None or module == '' or module.find('.') < 0):
            logger_name = 'root'  # Logger.MOD(1) |   __package__
        else:
            logger_name = module[0:module.rfind('.')]

        if duration is None:
            if context is None:
                duration = 0
            else:
                duration = Logger.LogContext.getPerfTime() - context.start_time

        Logger.getLogger(logger_name).log(Logger.Level.DEBUG,
                                          Logger.logMsg(module, Logger.FUNC(1), Logger.LINE(1),
                                                        Logger.LogEntryType.EXIT, duration, str(result),
                                                        msg, None,
                                                        Logger.LOCAL_VARS(1), stack_depth))



        if context is None:
            context = Logger.LogContext()

        return context

    def debug(msg: str = '',
              duration: int | None = None,
              result: Any | None = None,
              *,
              context: LogContext | None = None) -> LogContext:

        module: str | None = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

        stack_depth: int = 0
        if Logger._log_stack_depth == True:
            stack_depth = Logger.STACK_DEPTH(1)

        logger_name: str | None = None
        if (module is None or module == '' or module.find('.') < 0):
            logger_name = 'root'  # Logger.MOD(1) |   __package__
        else:
            logger_name = module[0:module.rfind('.')]

        if duration is None:
            if context is None:
                duration = 0
            else:
                duration = Logger.LogContext.getPerfTime() - context.start_time

        Logger.getLogger(logger_name).log(Logger.Level.DEBUG,
                                          Logger.logMsg(module, Logger.FUNC(1), Logger.LINE(1),
                                                        Logger.LogEntryType.STD, duration, str(result),
                                                        msg, None,
                                                        Logger.LOCAL_VARS(1), stack_depth))



        if (context is None):
            context = Logger.LogContext()
        return context

    def error(msg: str = '',
              duration: int | None = None,
              result: Any = '',
              exception: Exception | None = None,
              *,
              context: LogContext | None = None) -> LogContext:

        module: str | None = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

        stack_depth: int = 0
        if Logger._log_stack_depth == True:
            stack_depth = Logger.STACK_DEPTH(1)

        logger_name: str | None = None
        if (module is None or module == '' or module.find('.') < 0):
            logger_name = 'root'  # Logger.MOD(1) |   __package__
        else:
            logger_name = module[0:module.rfind('.')]

        if duration is None:
            if context is None:
                duration = 0
            else:
                duration = Logger.LogContext.getPerfTime() - context.start_time

        Logger.getLogger(logger_name).log(Logger.Level.ERROR,
                                          Logger.logMsg(module, Logger.FUNC(1), Logger.LINE(1),
                                                        Logger.LogEntryType.STD, duration, str(result),
                                                        msg, exception,
                                                        Logger.LOCAL_VARS(1), stack_depth))
        if (context is None):
            context = Logger.LogContext()
        return context

    def info(msg: str = '',
             duration: int | None = None,
             result: Any = '',
             *,
             context: LogContext | None = None) -> LogContext:

        module: str | None = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

        stack_depth: int = 0
        if Logger._log_stack_depth == True:
            stack_depth = Logger.STACK_DEPTH(1)

        logger_name: str | None = None
        if (module is None or module == '' or module.find('.') < 0):
            logger_name = 'root'  # Logger.MOD(1) |   __package__
        else:
            logger_name = module[0:module.rfind('.')]

        if duration is None:
            if context is None:
                duration = 0
            else:
                duration = Logger.LogContext.getPerfTime() - context.start_time

        Logger.getLogger(logger_name).log(Logger.Level.INFO,
                                          Logger.logMsg(module, Logger.FUNC(1), Logger.LINE(1),
                                                        Logger.LogEntryType.STD, duration, str(result),
                                                        msg, None,
                                                        Logger.LOCAL_VARS(1), stack_depth))
        if (context is None):
            context = Logger.LogContext()
        return context

    def critical(msg: str = '',
                 duration: int | None = None,
                 result: Any = '',
                 exception: Exception | None = None,
                 *,
                 context: LogContext | None = None) -> LogContext:

        module: str | None = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

        stack_depth: int = 0
        if Logger._log_stack_depth == True:
            stack_depth = Logger.STACK_DEPTH(1)

        logger_name: str | None = None
        if (module is None or module == '' or module.find('.') < 0):
            logger_name = 'root'  # Logger.MOD(1) |   __package__
        else:
            logger_name = module[0:module.rfind('.')]

        if duration is None:
            if context is None:
                duration = 0
            else:
                duration = Logger.LogContext.getPerfTime() - context.start_time

        Logger.getLogger(logger_name).log(Logger.Level.CRITICAL,
                                          Logger.logMsg(module, Logger.FUNC(1), Logger.LINE(1),
                                                        Logger.LogEntryType.STD, duration, str(result),
                                                        msg, exception,
                                                        Logger.LOCAL_VARS(1), stack_depth))
        if (context is None):
            context = Logger.LogContext()
        return context

    def warning(msg: str = '',
                duration: int | None = None,
                result: Any = '',
                exception: Exception | None = None,
                *,
                context: LogContext | None = None) -> LogContext:

        module: str | None = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

        stack_depth: int = 0
        if Logger._log_stack_depth == True:
            stack_depth = Logger.STACK_DEPTH(1)

        logger_name: str | None = None
        if (module is None or module == '' or module.find('.') < 0):
            logger_name = 'root'  # Logger.MOD(1) |   __package__
        else:
            logger_name = module[0:module.rfind('.')]

        if duration is None:
            if context is None:
                duration = 0
            else:
                duration = Logger.LogContext.getPerfTime() - context.start_time

        Logger.getLogger(logger_name).log(Logger.Level.WARNING,
                                          Logger.logMsg(module, Logger.FUNC(1), Logger.LINE(1),
                                                        Logger.LogEntryType.STD, duration, str(result),
                                                        msg, exception,
                                                        Logger.LOCAL_VARS(1), stack_depth))
        if (context is None):
            context = Logger.LogContext()
        return context

    def logMsg(module: str | None = '',
               func_name: str | None = None,
               source_lineno: int | None = None,
               op_type: int = LogEntryType.STD,
               duration: int | None = None,
               log_result: Any | None = None,
               msg: str | None = None,
               exception: Exception | None = None,
               caller_local_vars: str | None = None,
               stack_depth: int | None = None) -> str:
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
        :rtype: str

       """

        # Add exception details to the main log message
        exception_str = ''
        if exception is not None:
            trace = []
            tb = exception.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            exception_str = str({
                'type': type(exception).__name__,
                'message': str(exception),
                'trace': trace
            })


        if (msg is not None):
            msg = msg.replace('|', ',')

        if log_result is None:
            log_result_str = ''
        else:
            log_result_str: str = str(log_result)

        caller_local_vars_str = ''
        if op_type == Logger.LogEntryType.ENTRY:
            entry_type_str = 'Entry'
            if func_name!='<module>':
                caller_local_vars_str = str(caller_local_vars)
        elif op_type == Logger.LogEntryType.EXIT:
            entry_type_str = 'Exit'
        else:
            entry_type_str = '-'

        func_name_str = ''
        if func_name=='<module>':
            func_name_str = '__main__'
        else:
            func_name_str = func_name

        module_str = module

        duration_str = ''
        if duration is not None:
            duration_str = str(duration)

        result: str = f'{module}|{func_name_str}|{source_lineno}|{stack_depth}|{duration_str}|{entry_type_str}|{log_result_str}|{msg}|{caller_local_vars_str}|{exception_str}'

        # clean data in log entry
        for key, regex in Logger.SENSITIVE_DATA_PATTERN_LIST.items():
            result = re.sub(regex, '**redact**', result)

        return result


def logMe(level: int = logging.DEBUG, enter_msg: str | None = '', exit_msg: str | None = '', exp_msg: str | None = ''):
    """ Decorator to add log entry and exit log entries for the function. Also any exception thrown will be logged and rethrown

    Parameters:
    level (int): class Level - DEBUG|CRITICAL|ERROR|INFO|WARNING
    enter_msg (str): added to the function entry log entry
    exit_msg (str): added to the function exit log entry

    Returns:
    decorator: Returning value

   """

    def decorator(fun):

        def wrapper(*args, **kwargs) -> Any:
            result: Any | None = None

            function_name: str = fun.__name__  # Logger.FUNC(1)
            line_no: int = Logger.LINE(1)

            stack_depth: int = 0
            if Logger._log_stack_depth == True:
                stack_depth = Logger.STACK_DEPTH(1) + 1


            module: str = Logger.QUALIFIED_MOD(Logger.FILE(1), os.path.sep)

            logger_name: str | None = None
            if (module is None or module == '' or module.find('.') < 0):
                logger_name = 'root'  # Logger.MOD(1) |   __package__
            else:
                logger_name = module[0:module.rfind('.')]

            exception_raised = False
            exception: Exception | None = None
            start: int = time.perf_counter_ns()
            try:
                log_msg = 'Entering function'
                if enter_msg is not None or enter_msg != '':
                    log_msg = f'{enter_msg} - Entering function'

                Logger.getLogger(logger_name).log(level,
                                                  Logger.logMsg(module, function_name, line_no,
                                                                Logger.LogEntryType.ENTRY, 0, None,
                                                                log_msg, None,
                                                                f'{args} - {kwargs}', stack_depth))

                start: int = time.perf_counter_ns()
                result = fun(*args, **kwargs)

            except Exception as e:
                exception_raised = True
                exception = e
                raise
            finally:
                finish: int = time.perf_counter_ns()
                exe_duration: int = finish - start

                if exception_raised:
                    log_msg = f'Leaving function - completed WITH error: {exception.__str__()}'
                    if exp_msg is not None or exp_msg != '':
                        log_msg = f'{exp_msg} - Leaving function - completed WITH error: {exception.__str__()}'

                    Logger.getLogger(logger_name).log(Logger.Level.ERROR,
                                                        Logger.logMsg(module, function_name, line_no,
                                                                      Logger.LogEntryType.ENTRY, exe_duration, None,
                                                                      log_msg, exception,
                                                                      '', stack_depth))

                else:
                    log_msg = 'Leaving function - completed without error'
                    if exp_msg is not None or exp_msg != '':
                        log_msg = f'{exit_msg} - Leaving function - completed without error'

                    Logger.getLogger(logger_name).log(level,
                                                      Logger.logMsg(module, function_name, line_no,
                                                                    Logger.LogEntryType.EXIT, exe_duration, str(result),
                                                                    log_msg, None,
                                                                     '', stack_depth))

            return result

        return wrapper

    return decorator


"""
# TODOs
1. Add functions to create standard formatted log entries for the different type : entry , exit etc
2. filter for and clean sensitive data
"""
