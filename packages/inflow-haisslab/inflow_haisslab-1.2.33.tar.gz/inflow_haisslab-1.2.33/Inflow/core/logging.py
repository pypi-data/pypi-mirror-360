# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:06:28 2023

@author: tjostmou
"""

import sys, logging, datetime, inspect, os
from functools import wraps

# from logging.handlers import TimedRotatingFileHandler
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
from pathlib import Path

_LOGGING_STATUS = False


def get_local_logger(logger_name=None, silent=False):
    add_all_custom_headers()
    if logger_name is None:
        logger_name = inspect.stack()[1][3]
    if logger_name == "root":
        try:
            logger_name = inspect.stack()[2][3]
        except IndexError:
            pass
    local_log = logging.getLogger(logger_name)
    if silent:
        local_log.setLevel(logging.ERROR)
    return local_log


class CustomLogger(logging.Logger):
    def __init__(self, name, prefix="", level=logging.NOTSET):
        super().__init__(name, level)
        self.prefix = {"reference_holder": prefix}

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        if self.isEnabledFor(level):
            if prefix := self.get_prefix():
                msg = f"{prefix} {msg}"
            super()._log(level, msg, args, exc_info, extra, stack_info)

    def get_prefix(self, get_value=True):
        def return_reference(value):
            if get_value:
                return value["reference_holder"]
            return value

        if (
            self.parent is None
        ):  # we can't go higher this is where we should set the prefix to apply to everything downward
            return return_reference(self.prefix)
        else:
            return return_reference(self.parent.get_prefix(get_value=False))

    def set_prefix(self, value):
        self.get_prefix(get_value=False)["reference_holder"] = value

    def append_to_prefix(self, value):
        current_value = self.get_prefix(get_value=True)
        self.get_prefix(get_value=False)["reference_holder"] = current_value + value

    # def getChild(self, suffix):
    #     child_name = self.name + "." + suffix
    #     logger = self.manager.loggerDict.get(child_name)
    #     if logger is None:
    #         logger = self.__class__(child_name)
    #         self.manager.loggerDict[child_name] = logger
    #         self._fixupParents(child_name, logger)
    #         print("A child is born : " + child_name + str(logger))
    #     return logger


def enable_logging(mode="both", level="INFO"):
    level = level.upper()
    level = eval(f"logging.{level}")

    global _LOGGING_STATUS
    if _LOGGING_STATUS:
        logger = logging.getLogger("enable_logging")
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        logger.debug(f"Setting logger level to {level}")
        logger.debug("Logger is already configured, skipping instanciation")
        for handler in root_logger.handlers:
            handler.setLevel(level)
            logger.debug(f"setting {handler} handler level to {level}")
        return

    logging.setLoggerClass(CustomLogger)
    add_all_custom_headers()

    root_logger = CustomLogger("root")
    logging.Logger.manager.root = root_logger
    logging.root = root_logger

    if mode == "both" or "file":
        downloads_path = Path.home().joinpath("Downloads").joinpath(".python_logs")
        downloads_path.mkdir(parents=True, exist_ok=True)

        file_handler = ConcurrentTimedRotatingFileHandler(
            filename=downloads_path.joinpath("pylogs.log"),
            when="D",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        formatter = FileFormatter(fmt=FileFormatter.file_format, datefmt="%H:%M:%S")

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
        # root_logger.addHandler(file_handler)

    if mode == "both" or mode == "console":
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = ConsoleFormatter()

        formatter.update_formats()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        # root_logger.addHandler(console_handler)

    logging.getLogger().setLevel(level)
    _LOGGING_STATUS = True


def add_all_custom_headers():
    addLoggingLevel("LOAD_INFO", logging.INFO + 1, if_exists="keep")
    addLoggingLevel("SAVE_INFO", logging.INFO + 2, if_exists="keep")
    addLoggingLevel("INFO_HEADER", logging.INFO + 5, if_exists="keep")
    addLoggingLevel("INFO_CLOSE_HEADER", logging.INFO + 6, if_exists="keep")
    addLoggingLevel("INFO_OPEN_HEADER", logging.INFO + 7, if_exists="keep")


def addLoggingLevel(levelName, levelNum, methodName=None, if_exists="raise"):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName) or hasattr(logging, methodName) or hasattr(logging.getLoggerClass(), methodName):
        if if_exists == "keep":
            return
        if hasattr(logging, levelName):
            raise AttributeError("{} already defined in logging module".format(levelName))
        if hasattr(logging, methodName):
            raise AttributeError("{} already defined in logging module".format(methodName))
        if hasattr(logging.getLoggerClass(), methodName):
            raise AttributeError("{} already defined in logger class".format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


NAMELENGTH = 33
LEVELLENGTH = 10
MAX_FOLDERS = 4


class FileFormatter(logging.Formatter):
    file_format = (
        f"[%(asctime)s] - %(levelname)-{LEVELLENGTH}s : %(name)-{NAMELENGTH}s : %(message)s (line:%(lineno)d -"
        " file:%(pathname)s)"
    )

    def format(self, record):
        if "pathname" in record.__dict__.keys():
            if (sec_len := len(sections := record.pathname.split(os.path.sep))) > MAX_FOLDERS:
                record.pathname = "(...)" + os.path.sep.join(
                    [sections[sec_len - i] for i in reversed(range(1, MAX_FOLDERS + 1))]
                )

        return super().format(record)


class ConsoleFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    light_blue = "\x1b[94;20m"
    bold_light_blue = "\x1b[94;1m"
    purple = "\x1b[1;35m"
    deep_blue_over_purple_bold = "\x1b[38;5;57;48;5;195;1m"
    green = "\x1b[32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    simple_format = f"%(levelname)-{LEVELLENGTH}s : %(name)-{NAMELENGTH}s : %(message)s"
    header_format = f"%(name)-{NAMELENGTH}s : %(message)s - %(asctime)s "
    full_format = (
        f"%(levelname)-{LEVELLENGTH}s : %(name)-{NAMELENGTH}s : %(message)s (%(filename)s:%(lineno)d) - %(asctime)s"
    )

    opening_header_format = deep_blue_over_purple_bold + ("░" * (LEVELLENGTH + 2)) + " " + header_format

    FORMATS = {
        logging.DEBUG: grey + full_format + reset,
        logging.INFO: light_blue + simple_format + reset,
        logging.WARNING: yellow + full_format + reset,
        logging.ERROR: red + full_format + reset,
        logging.CRITICAL: bold_red + full_format + reset,
    }

    def update_formats(self):
        self.default_time_format = r"%Y/%m/%d %H:%M:%S"
        self.default_msec_format = None

        FORMATS = {
            logging.INFO_HEADER: self.bold_light_blue + self.header_format + self.reset,
            logging.LOAD_INFO: self.green + self.simple_format + self.reset,
            logging.SAVE_INFO: self.green + self.simple_format + self.reset,
            logging.INFO_CLOSE_HEADER: self.opening_header_format + "\n" + self.reset,
            logging.INFO_OPEN_HEADER: self.opening_header_format + self.reset,
        }

        self.FORMATS.update(FORMATS)

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LogContext:
    def __init__(self, context_msg, allow_multi_prefix=True):
        self.root_logger = logging.getLogger()
        if not isinstance(self.root_logger, CustomLogger):
            self._valid = False
            return
        self._valid = True
        self.initial_prefix = self.root_logger.get_prefix()
        self.context_msg = context_msg
        # \x1b[94;1m  \x1b[0m to set bold blue and then reset to black.
        # Sadly we loose initial formatting. Need to see how to fix that
        self.allow_multi_prefix = allow_multi_prefix

    def __enter__(self):
        if not self._valid:
            return
        if self.allow_multi_prefix:
            self.root_logger.append_to_prefix("<" + self.context_msg + ">")
        else:
            self.root_logger.set_prefix("<" + self.context_msg + ">")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._valid:
            return
        self.root_logger.set_prefix(self.initial_prefix)


class LogSession(LogContext):
    def __init__(self, session_details):
        message = "s#" + str(session_details.alias)
        super().__init__(message, allow_multi_prefix=False)


def session_log_decorator(func):
    @wraps(func)
    def wrapper(session_details, *args, **kwargs):
        if kwargs.get("no_session_log", False):
            return func(*args, **kwargs)
        with LogSession(session_details):
            return func(session_details, *args, **kwargs)

    return wrapper
