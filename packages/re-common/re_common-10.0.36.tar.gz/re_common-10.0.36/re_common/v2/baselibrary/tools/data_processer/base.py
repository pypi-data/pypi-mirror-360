from abc import ABC, abstractmethod
from typing import List, Generator


class BaseFileReader(ABC):

    def __init__(self, batch_size: int = 10000):
        self.batch_size = batch_size
        self.read_model = 1

    @abstractmethod
    def list_files(self, path: str) -> List[str]:
        """列出路径下所有目标文件"""
        pass

    @abstractmethod
    def count_lines(self, file_path: str) -> int:
        """统计文件行数"""
        pass

    @abstractmethod
    def read_lines(self, file_path: str) -> Generator[List[str], None, None]:
        """读取文件内容，返回批量数据"""
        pass

    @abstractmethod
    def read_all(self, file_path: str) -> List[List[str]]:
        """读取整个文件，默认按1000行分批"""
        return [line for line in self.read_lines(file_path)]

    def read_select(self, file_path: str) -> Generator[List[str], None, None]:
        if self.read_model == 1:
            for batch_data in self.read_lines(file_path):
                yield batch_data
        elif self.read_model == 2:
            for batch_data in self.read_all(file_path):
                yield batch_data
        else:
            raise Exception("模式选择错误")


class BaseFileWriter(ABC):

    def __init__(self, file_path: str, compress: bool = True, overwrite: bool = True, encoding: str = "utf-8"):
        self.file_path = file_path
        self.compress = compress
        self.encoding = encoding
        self.overwrite = overwrite

    @abstractmethod
    def write_lines(self, lines: List[str], file_path: str):
        """写入多行文本到文件，支持压缩"""
        pass
