import io
import warnings
from typing import Optional, Any
from .interface import ObjectInterface
from .func import FileStorageConfig

try:
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
except ImportError:
    warnings.warn("pip install cos-python-sdk-v5")


class CosImpl(ObjectInterface):

    def __init__(self, config: FileStorageConfig):
        self.bucket = config.fs_bucket
        self.client: CosS3Client = CosS3Client(CosConfig(Region=config.fs_region,
                                                         SecretId=config.fs_secret_id,
                                                         SecretKey=config.fs_secret_key,
                                                         Scheme=config.fs_scheme,
                                                         Endpoint=config.fs_endpoint))

    def upload(self,
               file_path_name: str,
               bytes_io: io.BytesIO,
               length: Optional[int] = None,
               metadata: Optional[dict] = None,
               **kwargs) -> str:
        etag = True if kwargs.get("etag", None) else False
        response = self.client.put_object(
            Bucket=self.bucket,
            Body=bytes_io,
            Key=file_path_name,
            EnableMD5=etag
        )
        return response['ETag']

    def download(self, file_path_name: str):
        res_dict = self.client.get_object(Bucket=self.bucket, Key=file_path_name)
        return res_dict['Body'].read()

    def object_exists(self, file_path_name: str) -> Optional[Any]:
        # cos 是返回 bool
        return self.client.object_exists(self.bucket, Key=file_path_name)
