import abc
import asyncio
import sys
from concurrent.futures import ProcessPoolExecutor
import gzip

import multiprocessing
from pathlib import Path

from io import BytesIO
import time
from typing import Awaitable, Callable, Any, Generator, List, Literal, Union

from hdfs import InsecureClient


from re_common.v2.baselibrary.tools.resume_tracker import ResumeTracker


_pool = None
_loop = None


class HDFSBaseProcessor(abc.ABC):
    def __init__(
        self,
        hdfs_dir: str,
        hdfs_url: str = "http://VIP-DC-MASTER-2:9870",
        hdfs_user: str = "root",
        db_path: Union[str, Path] = "processed_files.db",
        concurrency: int = 50,
        batch_size: int = 50,
        encoding: str = "utf-8",
        read_mode: Literal["all", "stream"] = "all",
        retries: int = 3,
        pool_factory: Callable[[], Awaitable[Any]] = None,
        max_processes: int = None,  # 添加多进程支持
        result_dir: str = None,
    ):
        self.hdfs_dir = hdfs_dir
        self.hdfs_url = hdfs_url
        self.hdfs_user = hdfs_user
        self.tracker = ResumeTracker(db_path)
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.encoding = encoding
        self.read_mode = read_mode
        self.retries = retries
        self.result_dir = result_dir
        self.pool_factory = pool_factory
        self.max_processes = max_processes or max(multiprocessing.cpu_count() - 1, 1)  # 默认使用CPU核心数-1
        self._client = None

        self.tracker.init_db()

    @property
    def client(self):
        if self._client is None:
            self._client = InsecureClient(self.hdfs_url, user=self.hdfs_user)
        return self._client

    async def _get_pool(self):
        if self.pool_factory is None:
            return None
        global _pool
        if _pool is None:
            _pool = await self.pool_factory()
        return _pool

    def _list_gz_files(self) -> List[str]:
        """列出 HDFS 目录中的所有 gzip 文件"""
        return [
            f"{self.hdfs_dir}/{file[0]}"
            for file in self.client.list(self.hdfs_dir, status=True)
            if file[0].endswith(".gz")
        ]

    def _count_total_lines(self, gz_file_path: str) -> int:
        with self.client.read(gz_file_path) as hdfs_file:
            with gzip.GzipFile(fileobj=hdfs_file) as gz:
                return sum(1 for _ in gz)

    def _batch_read_gz_stream(self, gz_file_path: str) -> Generator[List[str], Any, None]:
        """流式读取gz文件，分批yield返回"""
        with self.client.read(gz_file_path) as hdfs_file:
            with gzip.GzipFile(fileobj=hdfs_file) as gz:
                while True:
                    lines = []
                    for _ in range(self.batch_size):
                        try:
                            line = next(gz)
                            if line.strip():  # 移除空行
                                lines.append(line.decode(self.encoding))  # 解码
                        except StopIteration:  # 文件已读完
                            break
                    if not lines:
                        break
                    yield lines

    def _batch_read_gz_all(self, gz_file_path: str) -> List[List[str]]:
        """一次读取gz文件全部内容，二维数组批量返回"""
        with self.client.read(gz_file_path) as reader:  # 以二进制模式读取
            compressed_data = reader.read()  # 读取压缩数据
            with gzip.GzipFile(fileobj=BytesIO(compressed_data)) as gz_file:  # 解压缩
                content = gz_file.read().decode(self.encoding)  # 解码为字符串
                print(f"文件读取成功: {gz_file_path}")
                lines = [i for i in content.split("\n") if i.strip()]
                batch_lines = [lines[i : i + self.batch_size] for i in range(0, len(lines), self.batch_size)]
                return batch_lines

    def _batch_read_gz(self, gz_file_path: str):
        # 这里根据不同的配置选用不同的读取文件的方法
        if self.read_mode == "stream":
            return self._batch_read_gz_stream(gz_file_path)
        else:
            return self._batch_read_gz_all(gz_file_path)

    def _generate_write_data(self, results):
        for res in results:
            yield str(res) + "\n"

    def _print_progress(self, file_path, processed_lines, total_lines, start_time, processing_start_time):
        elapsed_time = time.perf_counter() - start_time  # 已用时间
        processing_time = time.perf_counter() - processing_start_time  # 本次处理时间
        avg_processing_time = (
            (elapsed_time * 1000) / processed_lines if processed_lines > 0 else float("inf")
        )  # 平均每条数据的处理时间（毫秒）
        # 估算剩余时间
        remaining_time = (
            ((avg_processing_time / 1000) * (total_lines - processed_lines)) if processed_lines > 0 else float("inf")
        )
        # 显示进度信息
        print(
            f"文件: {file_path} 总进度: {processed_lines}/{total_lines} 行 | "
            f"已用时间: {elapsed_time:.2f}秒 | 本次处理时间: {processing_time:.2f}秒 | "
            f"预估剩余时间: {remaining_time:.2f}秒 | 平均每条处理时间: {avg_processing_time:.2f}毫秒"
        )

    def _print_final_progress(self, file_path, processed_lines, total_lines, start_time):
        final_elapsed_time = time.perf_counter() - start_time  # 最终已用时间
        print(
            f"文件: {file_path} 处理完成 | 总进度: {processed_lines}/{total_lines} 行 | "
            f"总已用时间: {final_elapsed_time:.2f}秒 | "
            f"平均每条处理时间: {(final_elapsed_time * 1000) / processed_lines:.2f}毫秒"
            if processed_lines > 0
            else "处理无数据"
        )

    @abc.abstractmethod
    async def _process_file(self, hdfs_file_path, process_func):
        pass

    async def _retry_process_file(self, hdfs_file_path, process_func):
        """带重试机制的文件处理"""
        retry_count = 0
        while retry_count < self.retries:
            try:
                if self.tracker.is_processed(hdfs_file_path):
                    print(f"跳过已处理文件: {hdfs_file_path}")
                    return True
                await self._process_file(hdfs_file_path, process_func)
                self.tracker.mark_processed(hdfs_file_path)  # 标记文件已处理
                return True  # 成功处理后退出
            except Exception as e:
                retry_count += 1
                print(f"处理文件 {hdfs_file_path} 时发生错误: {e}，正在重试 {retry_count}/{self.retries}")
                await asyncio.sleep(2**retry_count)
        print(f"处理文件 {hdfs_file_path} 失败，达到重试上限")
        return False

    def _process_file_wrapper(self, args):
        """为多进程执行准备的同步包装函数"""
        hdfs_file_path, process_func = args
        if sys.platform == "win32":
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._retry_process_file(hdfs_file_path, process_func))
        else:
            global _loop
            if _loop is None:
                _loop = asyncio.new_event_loop()
                asyncio.set_event_loop(_loop)
            return _loop.run_until_complete(self._retry_process_file(hdfs_file_path, process_func))

    async def _run_multi_process(self, gz_files, process_func):
        """多进程并发运行文件处理任务"""
        args_list = [(file_path, process_func) for file_path in gz_files]
        with ProcessPoolExecutor(max_workers=self.max_processes) as executor:
            # return executor.map(self._process_file_wrapper, args_list)
            loop = asyncio.get_running_loop()
            self._client = None  # 避免连接对象无法序列化导致卡死
            tasks = [loop.run_in_executor(executor, self._process_file_wrapper, args) for args in args_list]
            results = await asyncio.gather(*tasks)

        if all(results):
            # 处理完成后清理断点记录
            self.tracker.clear_processed_items()
            print(f"已清空断点记录: {self.tracker.db_path}")
            return results
        else:
            raise Exception("部分或全部文件处理失败")

    @abc.abstractmethod
    async def map(self, process_func: Callable[[Any, Any], Awaitable[Any]]) -> None:
        pass
