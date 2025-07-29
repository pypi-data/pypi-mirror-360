import functools
import time
import logging
import asyncio

logger = logging.getLogger("activefence_client_sdk")



def retry_with_exponential_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries (int): Maximum number of retries
        base_delay (float): Base delay for exponential backoff in seconds
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error("Failed after %s retries: %s", max_retries, e)
                        raise e

                    # Calculate delay with exponential backoff (no jitter)
                    delay = base_delay * (2 ** (retries - 1))

                    logger.warning(
                        "Attempt %s failed with error: %s. Retrying in %.2f seconds...",
                        retries,
                        e,
                        delay,
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


def async_retry_with_exponential_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retrying an async function with exponential backoff.

    Args:
        max_retries (int): Maximum number of retries
        base_delay (float): Base delay for exponential backoff in seconds
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error("Failed after %s retries: %s", max_retries, e)
                        raise e

                    # Calculate delay with exponential backoff (no jitter)
                    delay = base_delay * (2 ** (retries - 1))

                    logger.warning(
                        "Attempt %s failed with error: %s. Retrying in %.2f seconds...",
                        retries,
                        e,
                        delay,
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator
