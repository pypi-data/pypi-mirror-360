
import asyncio
import base64
import warnings
import httpx
from typing import Dict, Optional, List, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from kitx.__about__ import env_prefix
"""
    接入 openobserve 的方法
"""


class ObserveConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=env_prefix)
    """
    Observe配置
    """
    observe_host: str = 'py-observe'
    observe_port: int = 5080
    observe_base_dir: str = "/logs"
    observe_username: str = 'root@example.com'
    observe_password: str = 'observeAdmin123123'
    observe_organization: str = "test"  # 项目名
    observe_stream: str = "dev"  # 环境+版本等

    @property
    def authorization(self) -> str:
        return f"Basic {base64.b64encode(bytes(self.observe_username + ':' + self.observe_password, 'utf-8')).decode('utf-8')}"

    @property
    def base_url(self) -> str:
        return f"http://{self.observe_host}:{self.observe_port}{self.observe_base_dir}/api"

    @property
    def log_url(self) -> str:
        if not self.observe_organization:
            raise Exception("缺少配置: observe_organization， 请设置环境变量observe_organization=xx或初始化")
        if not self.observe_stream:
            raise Exception("缺少配置: observe_stream， 请设置环境变量observe_stream=xx或初始化")
        return f"{self.base_url}/{self.observe_organization}/{self.observe_stream}/_json"

    @property
    def trace_url(self) -> str:
        if not self.observe_organization:
            raise Exception("缺少配置: observe_organization， 请设置环境变量observe_organization=xx或初始化")
        if not self.observe_stream:
            raise Exception("缺少配置: observe_stream， 请设置环境变量observe_stream=xx或初始化")
        return f"{self.base_url}/{self.observe_organization}/{self.observe_stream}/traces"


class ObServe:

    def __init__(self, conf: Optional[ObserveConfig] = None):
        self.config = conf if conf else ObserveConfig()
        self.authorization = self.config.authorization
        self.log_url = self.config.log_url
        self.service_status = True
        # 初始化连接池
        self.httpx_client = httpx.AsyncClient(timeout=0.5,
                                              limits=httpx.Limits(max_connections=100, max_keepalive_connections=100))

    async def send_(self, data: Any):
        try:
            if not self.service_status:
                warnings.warn(f"检测日志平台不可用: 暂停上传")
                return
            req = httpx.Request(url=self.log_url,
                                method="POST",
                                headers={"Authorization": self.authorization},
                                json=data)
            res = await self.httpx_client.send(req)
            print(res.status_code)
            if res.status_code != 200:
                warnings.warn(f"推送日志平台异常: {res.status_code}")
                self.service_status = False
        except Exception as e:
            msg = f"日志采集报错: {e}"
            warnings.warn(msg)
            self.service_status = False

    def send(self, data: Any):
        asyncio.create_task(self.send_(data))
