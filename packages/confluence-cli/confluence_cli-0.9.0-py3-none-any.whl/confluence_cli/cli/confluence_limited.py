import logging
import time
from functools import wraps
from typing import Any

from confluence_cli.cli import ConfluenceWrapper
from confluence_cli.cli.utils import (
    secure_call_func,
    base_methods_decorator,
)

logger = logging.getLogger(__name__)

#
MIN_TIME_BETWEEN_CALLS: float = 2.0
last_access_time: float = 0.0


def param_limit_rate(min_time_between_calls: float = MIN_TIME_BETWEEN_CALLS) -> callable:
    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            global last_access_time
            tick: float = time.perf_counter()
            t = tick - last_access_time
            if last_access_time != 0.0 and t < min_time_between_calls:
                sleep_time = min_time_between_calls - t
                logger.debug(
                    f"RateBrake: Time since last Confluence API access: {tick - last_access_time}"
                    f"s : sleeping: {sleep_time}"
                )
                time.sleep(sleep_time)
            last_access_time = time.perf_counter()
            # * No exception handling here
            result = secure_call_func(func)(*args, **kwargs)
            return result

        return wrapper

    return decorator


def limit_rate(func) -> callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        global last_access_time
        tick: float = time.perf_counter()
        t = tick - last_access_time
        if last_access_time != 0.0 and t < MIN_TIME_BETWEEN_CALLS:
            sleep_time = MIN_TIME_BETWEEN_CALLS - t
            logger.debug(
                f"RateBrake: Time since last Confluence API access:  {tick - last_access_time} s : "
                f"sleeping: {sleep_time}"
            )
            time.sleep(sleep_time)
        last_access_time = time.perf_counter()
        # * No exception handling here
        result = secure_call_func(func)(*args, **kwargs)
        return result

    return wrapper


@base_methods_decorator(
    deco=param_limit_rate(min_time_between_calls=MIN_TIME_BETWEEN_CALLS),
    regex=r"(post|put|delete|get)", base_class=ConfluenceWrapper
)
class ConfluenceLimitedWraper(ConfluenceWrapper):
    """Limited access ratio Confluence client. Valid only for non-concurrent non-parallel access"""
