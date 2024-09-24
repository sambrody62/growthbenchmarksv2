import functools
import time
from flask import current_app


def logging(func):
    """
    A decorator that wraps the passed in function and logs 
    exceptions should one occur
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()

        logger = current_app.logger

        logger.info(f"Function: {func.__name__}") 
        logger.debug(f"Arguments:\n{args}\n-----\n{kwargs}\n-----")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Result:\n{result}\n-----")
            return result
        except Exception as e:
            # log the exception
            logger.exception(f"Exception: {e}")

            # re-raise the exception
            raise
        finally:
            end = time.time()
            
            logger.debug(f"""Time: {start} -> {end} = {end - start}""")

    return wrapper