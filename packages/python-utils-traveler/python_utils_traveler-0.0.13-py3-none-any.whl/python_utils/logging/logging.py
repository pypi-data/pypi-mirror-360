import logging
import time

_logger = None

def init_logger():
    '''
    Description: Initializes logger

    Args: None

    Returns: None
    '''
    global _logger
    if _logger is None:
        # Create a formatter with a custom date and time format
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(pathname)s][%(funcName)s] | %(message)s', datefmt='%Y-%m-%d %H:%M:%S UTC')
        formatter.converter = time.gmtime

        # Create a stream handler and set the formatter
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Create a logger instance for common package
        _logger = logging.getLogger(__name__)
        _logger.addHandler(stream_handler)
        _logger.setLevel(logging.INFO)

    return _logger
