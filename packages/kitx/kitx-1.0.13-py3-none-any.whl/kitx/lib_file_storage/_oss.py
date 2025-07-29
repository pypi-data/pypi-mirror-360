import io
from typing import Optional

from .func import FileStorageConfig
from .interface import ObjectInterface


class OssImpl(ObjectInterface):

    def __init__(self, c: FileStorageConfig):
        self.bucket = c.fs_bucket
        self.client = None

    def upload(self,
               file_path_name: str,
               bytes_io: io.BytesIO,
               length: Optional[int] = None,
               metadata=None,
               **kwargs):
        pass


    def download(self, file_path_name: str) -> str:
        pass
