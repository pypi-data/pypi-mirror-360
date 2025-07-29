import io
from typing import Optional, ClassVar, Literal, Any
from ..__about__ import env_prefix
from .interface import ObjectInterface
from pydantic_settings import BaseSettings, SettingsConfigDict

from enum import Enum



class FileStorageType(Enum):
    OSS = "oss"
    Minio = "minio"
    COS = "cos"


class FileStorageConfig(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_prefix=env_prefix,
                                                                    use_enum_values=True)

    # env "kitx_fs_endpoint"
    # env "kitx_fs_secret_id"
    fs_type: FileStorageType = FileStorageType.COS.value
    fs_endpoint: str = "cos.ap-guangzhou.myqcloud.com"
    fs_secret_id: str = "xx"
    fs_secret_key: str = "xx"
    fs_bucket: str = "xx"
    fs_scheme: str = "https"
    fs_region: str = 'ap-guangzhou'
    fs_secure: bool = False


def get_interface_client(c: FileStorageConfig) -> ObjectInterface:
    if c.fs_type == FileStorageType.COS.value:
        from ._cos import CosImpl
        return CosImpl(c)

    elif c.fs_type == FileStorageType.Minio.value:
        from ._minio import MinioImpl
        return MinioImpl(c)

    elif c.fs_type == FileStorageType.OSS.value:
        from ._oss import OssImpl
        return OssImpl(c)
    else:
        raise TypeError(f"Unsupported file storage type: {c.type}")


def object_upload(obj: ObjectInterface,
                  file_path_name: str,
                  bytes_io: io.BytesIO,
                  length: Optional[int],
                  metadata=None,
                  **kwargs):
    return obj.upload(file_path_name, bytes_io, length, metadata, **kwargs)


def object_download(obj: ObjectInterface, file_path_name: str):
    return obj.download(file_path_name)


def object_exists(obj: ObjectInterface, file_path_name: str) -> Optional[Any]:
    return obj.object_exists(file_path_name)
