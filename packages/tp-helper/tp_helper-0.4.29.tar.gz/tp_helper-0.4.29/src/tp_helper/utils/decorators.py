import asyncio
import functools
import inspect
from collections import defaultdict


def retry_forever(start_message: str, error_message: str, delay: int = 10):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind(self, *args, **kwargs)
            parameters = bound.arguments
            formatted_start_message = start_message.format_map(defaultdict(str, **parameters))
            self.logger.debug(formatted_start_message)
            while True:
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    self.logging_error(e, error_message)
                await asyncio.sleep(delay)

        return wrapper

    return decorator
