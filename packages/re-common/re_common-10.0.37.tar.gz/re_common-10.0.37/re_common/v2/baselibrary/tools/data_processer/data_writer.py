import gzip
from io import BytesIO
from typing import List

from hdfs import InsecureClient

from re_common.v2.baselibrary.tools.data_processer.base import BaseFileWriter


class HDFSFileWriter(BaseFileWriter):
    def __init__(self, file_path: str, hdfs_url: str, hdfs_user: str, *args, **kwargs):
        super().__init__(file_path, *args, **kwargs)
        self.client = InsecureClient(hdfs_url, user=hdfs_user)

    def write_lines(self, lines: List[str], file_path: str = None):
        if file_path is None:
            file_path = self.file_path
        data = "\n".join(lines).encode(self.encoding)
        if self.compress:
            buf = BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
                gz.write(data)
            buf.seek(0)
            self.client.write(file_path, data=buf, overwrite=self.overwrite)
        else:
            self.client.write(file_path, data=data, overwrite=self.overwrite)


class LocalFileWriter(BaseFileWriter):
    def write_lines(self, lines: List[str], file_path: str, compress: bool = True, encoding="utf-8"):
        if compress:
            with gzip.open(file_path, 'wt', encoding=encoding) as f:
                for line in lines:
                    f.write(f"{line}\n")
        else:
            with open(file_path, 'w', encoding=encoding) as f:
                for line in lines:
                    f.write(f"{line}\n")
