import functools
import logging


def log_function(logger=None, level=logging.INFO):
    """Decorator that logs a noticable visual separator before
    running the decorated function. Useful for getting log output
    organized.

    Args:
        logger (Logger): logger to use when displaying the separator.
            If no logger is supplied, the text is printed instead.
        level (int): logging level to use if a logger is supplied.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            message = f" Running: {func.__name__} ".ljust(80, "#")
            if logger is not None:
                logger.log(level, message)
            else:
                print(message)
            return func(*args, **kwargs)

        return wrapper

    return decorator
