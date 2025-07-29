import functools
import time
from typing import Callable, Any, Coroutine


def async_logging_decorator(logging, logs: bool = False):
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            has_time = time.time() - start_time
            if logs:
                str_result = str(result)
                if len(str_result) > 1000:
                    str_result = str_result[:1000] + "..."
                logging.info(f"func:{func.__name__},执行时间: {has_time:.2f}秒, 入参:{args}{kwargs}，出参:{str_result}")
            else:
                logging.info(f"func:{func.__name__},执行时间: {has_time:.2f}秒")
            return result

        return wrapper

    return decorator


def logging_decorator(logging, logs: bool = False):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            has_time = time.time() - start_time
            if logs:
                str_result = str(result)
                if len(str_result) > 1000:
                    str_result = str_result[:1000] + "..."
                logging.info(f"func:{func.__name__},执行时间: {has_time:.2f}秒, 入参:{args}{kwargs}，出参：{str_result}")
            else:
                logging.info(f"func:{func.__name__},执行时间: {has_time:.2f}秒")
            return result

        return wrapper

    return decorator
