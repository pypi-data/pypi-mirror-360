import asyncio
import functools
import time
import traceback
import logging
from typing import Optional, Callable, Awaitable, Union, Tuple, Dict

Callback = Optional[Callable[[Exception, int, Tuple, Dict], Union[Awaitable, None]]]

logger = logging.getLogger('func_retry')


class MaxRetryError(Exception):
    def __init__(self, message, errors, **kwargs):
        super().__init__(message)
        self.errors = errors


def retry(exc=Exception, times: Optional[int] = 3, delay: Optional[int] = None,
          print_exc:bool = False, callback: Callback = None):
    """
    Retry

    Args:
        exc : **Exception** Exception or Subclass of Exception
        times : **Optional[int]** Max retry times. Default to **3**.
            When set to `None`, it will continue to retry until successful
        delay: **Optional[int]** Delay seconds. Default to **None**.
        print_exc: **bool** Show error info. Default to **False**
        callback: **Optional[Callable[[Exception, int, Tuple, Dict], Union[Awaitable, None]]]**

    Returns:

    """

    def do_try(current_times, total_times):
        if total_times is None:
            return True
        return current_times <= total_times

    def decorator_retry(func):
        @functools.wraps(func)
        async def async_retry(*args, **kwargs):
            current_retry_times = 0
            errors = []
            error_traceback = ''
            while do_try(current_retry_times, times):
                try:
                    return await func(*args, **kwargs)
                except exc as e:
                    if callback:
                        await callback(e, current_retry_times, args, kwargs)
                    current_retry_times += 1
                    errors.append(e)
                    error_traceback += f"[{current_retry_times - 1}] {traceback.format_exc()}\n"
                    logger.error(f'Run {func.__name__} error:\n'+traceback.format_exc(),stacklevel=2)
                    if print_exc:
                        traceback.print_exc()
                    if delay:
                        await asyncio.sleep(delay)
            raise MaxRetryError(f"{error_traceback}\nThe maximum number of retries has been reached",
                                errors=errors)

        @functools.wraps(func)
        def sync_retry(*args, **kwargs):
            current_retry_times = 0
            errors = []
            error_traceback = ''
            while do_try(current_retry_times, times):
                try:
                    return func(*args, **kwargs)
                except exc as e:
                    if callback:
                        callback(e, current_retry_times, args, kwargs)
                    current_retry_times += 1
                    errors.append(e)
                    error_traceback += f"[{current_retry_times - 1}] {traceback.format_exc()}\n"

                    logger.error(f'Try run {func.__name__} error, error info:\n'+traceback.format_exc(),stacklevel=2)
                    if print_exc:
                        traceback.print_exc()
                    if delay:
                        time.sleep(delay)
            raise MaxRetryError(f"{error_traceback}\nThe maximum number of retries has been reached",
                                errors=errors)

        # 判断函数是否为异步函数
        if asyncio.iscoroutinefunction(func):
            return async_retry
        else:
            return sync_retry

    return decorator_retry
