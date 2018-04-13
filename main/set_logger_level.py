"""
This file contains a helper function used by
functions across the Cortix project to set
the level of the logger.
"""

import logging

def set_logger_level(handler, handler_name, handler_level):
    """
    This is a helper function that
    takes in a file/console handler
    and sets its logger level accordingly.
    """

    if handler_level == 'DEBUG':
        handler.setLevel(logging.DEBUG)
    elif handler_level == 'INFO':
        handler.setLevel(logging.INFO)
    elif handler_level == 'WARN':
        handler.setLevel(logging.WARN)
    elif handler_level == 'ERROR':
        handler.setLevel(logging.ERROR)
    elif handler_level == 'CRITICAL':
        handler.setLevel(logging.CRITICAL)
    elif handler_level == 'FATAL':
        handler.setLevel(logging.FATAL)
    else:
        assert False, "File handler log level for %r: %r invalid"\
            % (handler_name, handler_level)

    return handler
