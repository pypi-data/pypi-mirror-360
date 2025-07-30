
### 算法内部 统一日志平台

#### 默认版本
```text
from lib_logging import logger, LoggerInitializer, ObServe, ObserveConfig
logger.info("xx")
```


#### 日志平台用法 (结合web框架)
```
def my_filter(log: Dict):
    log["trace_id"] = TraceCtx.get_id()
    return log, ["trace_id"]

format_str = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    '<level>{trace_id}</level> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
    '<level>{message}</level>'
)

logger = LoggerInitializer(ObServe(ObserveConfig(
    observe_host='172.20.0.2',
    observe_port=40000,
    observe_base_dir="/logs",
    observe_username='root@isigning.com',
    observe_password='axzx@2025',
    observe_organization="algo_handwriting_database",  # 项目名
    observe_stream="dev")  # 版本等
)).init_log(format_str=format_str, filter_func=my_filter)

logger.info("LoggerInitializer-----format_str---my_filter---")
```

#### 装饰器用法

```text
@async_logging_decorator(logger)
async def async_function(a, b):
    logger.info(f"执行异步函数，参数: {a}, {b}")
    await asyncio.sleep(1)
    return a + b
```


#### 日志平台用法 (默认无trace_id)
```
from lib_logging import async_logging_decorator, LoggerInitializer, ObServe, ObserveConfig
logger = LoggerInitializer(ObServe(ObserveConfig(
    observe_host='172.20.0.2',
    observe_port=40000,
    observe_base_dir="/logs",
    observe_username='root@isigning.com',
    observe_password='axzx@2025',
    observe_organization="lib_xxx",  # 项目名
    observe_stream="dev"  # 环境+版本等
))).init_log()
```