
import sys
from loguru import logger as _logger
from typing import Optional, Callable
from ._openobserve import ObServe


class LoggerInitializer:
    def __init__(self, ob_serve: Optional[ObServe] = None):
        self.oo = ob_serve if ob_serve else None
        self.filter_func = None

    def __filter(self, log: dict):
        log_json = {
            "time": log["time"].__str__(),
            "level": log['level'].name,
            "function": log['function'],
            "line": log['line'],
            "message": log['message'],
        }

        if self.filter_func:
            log, update_oo_key_list = self.filter_func(log)
            if not log or not isinstance(log, dict):
                raise Exception("[lib_logging] filter_func impl error")

            for key in update_oo_key_list:
                log_json.update({key: log.get(key)})

        if self.oo:  # 如果配置了日志平台 就发送
            self.oo.send(log_json)  # 内部异步任务发送
        return log

    def init_log(self, format_str: Optional[str] = None, filter_func: Optional[Callable] = None):
        """
            format_str:
                format_str = (
                '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                '<level>{level: <8}</level> | '
                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
                '<level>{message}</level>'
            )

            filter_func:
                def filter(log: Dict):
                    ... do something
                    ... example:
                    log["trace_id"] = "xx"
                    return log , ["trace_id"]
        """
        if filter_func:
            self.filter_func = filter_func

        if not format_str:
            format_str = (
                '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                '<level>{level: <8}</level> | '
                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
                '<level>{message}</level>'
            )
        _logger.remove()
        _logger.add(sys.stderr, filter=self.__filter, format=format_str, enqueue=True)
        return _logger


# 初始化日志处理器
logger = LoggerInitializer().init_log()
