import functools
import logging
import sys
import time
from typing import Any
from collections.abc import Callable

from cloe_logging.formatters import DevOpsFormatter


def filter_arg_logger(arg: Any) -> bool:
    """
    Filter out all arguments that shall NOT be printed, i.e.,
    - strings with more than 25 characters
    - dictionaries
    - logging.Logger instances
    """
    match arg:
        case str() if len(arg) >= 25:
            result = False
        case dict():
            result = False
        case logging.Logger():
            result = False
        case _:
            result = True
    return result


def init_logging() -> logging.Logger:
    logger = logging.getLogger("azure-pipeline-logger")
    logger.setLevel(logging.INFO)
    section_formatter = DevOpsFormatter(section_info=True)
    section_handler = logging.StreamHandler()
    section_handler.setFormatter(section_formatter)
    logger.addHandler(section_handler)
    return logger


def build_logger():
    def log_decorator_info(func: Callable):
        @functools.wraps(func)
        def log_decorator_wrapper(*args, **kwargs):
            logger = init_logging()
            args_passed_in_function = [repr(a) for a in args if filter_arg_logger(a)]
            kwargs_passed_in_function = [f"{k}={v!r}" for k, v in kwargs.items()]
            formatted_arguments = ", ".join(args_passed_in_function + kwargs_passed_in_function)

            logger.info(f"##### START {func.__name__} WITH args [ {formatted_arguments} ] #####\n")

            try:
                start = time.time()
                value = func(*args, **kwargs)
                end = time.time()
                logger.info(f"\n##### END {func.__name__} DURATION [ '{round(end-start)}'s ] #####")
            except:
                logger.error(f"ERROR: {str(sys.exc_info()[1])}")
                raise
            return value

        return log_decorator_wrapper

    return log_decorator_info
