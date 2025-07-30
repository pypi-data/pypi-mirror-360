import gzip
import io
import json
from io import BytesIO
from pathlib import Path
from typing import List, Generator

import pandas as pd
from hdfs import InsecureClient

from re_common.v2.baselibrary.tools.data_processer.base import BaseFileReader


class HDFSFileReader(BaseFileReader):
    def __init__(self, batch_size: int = 1000, hdfs_url: str = "http://VIP-DC-MASTER-2:9870", hdfs_user: str = "root"):
        super().__init__(batch_size)
        self.client = InsecureClient(hdfs_url, user=hdfs_user)

    def list_files(self, path: str) -> List[str]:
        return [f"{path}/{f[0]}" for f in self.client.list(path, status=True) if f[0] != '_SUCCESS']

    def count_lines(self, file_path: str) -> int:
        with self.client.read(file_path) as f:
            return sum(1 for _ in f)

    def read_lines(self, file_path: str) -> Generator[List[str], None, None]:
        # 批量读取后 处理 缺点 连接可能会断
        with self.client.read(file_path) as f:
            while True:
                batch = []
                for _ in range(self.batch_size):
                    try:
                        line = next(f)
                        line = line.decode('utf-8')
                        if line.strip():
                            batch.append(line.strip())
                    except StopIteration:
                        break
                if not batch:
                    break
                yield batch

    def read_all(self, file_path: str) -> List[List[str]]:
        # 一次读取返回所有后批量处理缺点 内存占用
        with self.client.read(file_path) as f:
            lines = [line.decode('utf-8').strip() for line in f if line.decode('utf-8').strip()]
            return [lines[i: i + self.batch_size] for i in range(0, len(lines), self.batch_size)]


class HDFSGZFileReader(BaseFileReader):
    def __init__(self, batch_size: int = 1000, hdfs_url: str = "http://VIP-DC-MASTER-2:9870", hdfs_user: str = "root"):
        super().__init__(batch_size)
        self.hdfs_url = hdfs_url
        self.hdfs_user = hdfs_user
        self.client = None

    def _init_client(self):
        if self.client is None:
            self.client = InsecureClient(self.hdfs_url, user=self.hdfs_user)
        return self

    def list_files(self, path: str) -> List[str]:
        self._init_client()
        return [f"{path}/{f[0]}" for f in self.client.list(path, status=True) if f[0].endswith(".gz")]

    def count_lines(self, file_path: str) -> int:
        self._init_client()
        with self.client.read(file_path) as f:
            with gzip.GzipFile(fileobj=f) as gz:
                return sum(1 for _ in gz)

    def read_lines(self, file_path: str) -> Generator[List[str], None, None]:
        self._init_client()
        # 批量读取后 处理 缺点 连接可能会断
        with self.client.read(file_path) as f:
            with gzip.GzipFile(fileobj=f) as gz:
                while True:
                    batch = []
                    for _ in range(self.batch_size):
                        try:
                            line = next(gz)
                            if line.strip():
                                batch.append(line.decode("utf-8"))
                        except StopIteration:
                            break
                    if not batch:
                        break
                    yield batch

    def read_all(self, file_path: str) -> List[List[str]]:
        self._init_client()
        # 一次读取返回所有后批量处理缺点 内存占用
        with self.client.read(file_path) as reader:
            compressed_data = reader.read()
            with gzip.GzipFile(fileobj=BytesIO(compressed_data)) as gz_file:
                content = gz_file.read().decode("utf-8")
                lines = [i for i in content.split("\n") if i.strip()]
                return [lines[i: i + self.batch_size] for i in range(0, len(lines), self.batch_size)]


class HDFSParquetFileReader(BaseFileReader):
    def __init__(self, batch_size: int = 1000, hdfs_url: str = "http://VIP-DC-MASTER-2:9870", hdfs_user: str = "root"):
        super().__init__(batch_size)
        self.client = InsecureClient(hdfs_url, user=hdfs_user)

    def list_files(self, path: str) -> List[str]:
        return [f"{path}/{f[0]}" for f in self.client.list(path, status=True) if f[0].endswith(".parquet")]

    def count_lines(self, file_path: str) -> int:
        with self.client.read(file_path) as f:
            data = f.read()
            df = pd.read_parquet(io.BytesIO(data))
        count = len(df)
        return count

    def read_lines(self, file_path: str) -> Generator[List[str], None, None]:
        # 批量读取后 处理 缺点 连接可能会断
        with self.client.read(file_path) as f:
            data = f.read()
            df = pd.read_parquet(io.BytesIO(data))
            records = [json.dumps(row, ensure_ascii=False) for row in df.to_dict(orient='records')]
            for i in range(0, len(records), self.batch_size):
                yield records[i: i + self.batch_size]

    def read_all(self, file_path: str) -> List[List[str]]:
        # 一次读取返回所有后批量处理缺点 内存占用
        with self.client.read(file_path) as f:
            data = f.read()
            df = pd.read_parquet(io.BytesIO(data))
            records = [json.dumps(row, ensure_ascii=False) for row in df.to_dict(orient='records')]
            return [records[i: i + self.batch_size] for i in range(0, len(records), self.batch_size)]


class LocalGZFileReader(BaseFileReader):
    def list_files(self, path: str) -> List[str]:
        return [str(p) for p in Path(path).rglob("*.gz")]

    def count_lines(self, file_path: str) -> int:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            return sum(1 for _ in f)

    def read_lines(self, file_path: str) -> Generator[List[str], None, None]:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            while True:
                batch = []
                for _ in range(self.batch_size):
                    line = f.readline()
                    if not line:
                        break
                    if line.strip():
                        batch.append(line.strip())
                if not batch:
                    break
                yield batch

    def read_all(self, file_path: str) -> List[List[str]]:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return [lines[i: i + self.batch_size] for i in range(0, len(lines), self.batch_size)]


class LocalFileReader(BaseFileReader):
    def list_files(self, path: str) -> List[str]:
        return [str(p) for p in Path(path).rglob("*") if p.is_file()]

    def count_lines(self, file_path: str) -> int:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)

    def read_lines(self, file_path: str) -> Generator[List[str], None, None]:
        with open(file_path, 'r', encoding='utf-8') as f:
            while True:
                batch = []
                for _ in range(self.batch_size):
                    line = f.readline()
                    if not line:
                        break
                    if line.strip():
                        batch.append(line.strip())
                if not batch:
                    break
                yield batch

    def read_all(self, file_path: str) -> List[List[str]]:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return [lines[i: i + self.batch_size] for i in range(0, len(lines), self.batch_size)]
