import time

from python_utils.logging.logging import init_logger

logger = init_logger()

def timeit(fn):
    '''
    Description: decorator function that times the functions process time

    Args:
        - fn: the function being passed
    '''
    # *args and **kwargs are to support positional and named arguments of fn
    def get_time(*args, **kwargs): 
        start = time.time() 
        output = fn(*args, **kwargs)
        logger.info(f"Time taken in {fn.__name__}: {time.time() - start:.7f}")
        return output  # make sure that the decorator returns the output of fn
    return get_time 