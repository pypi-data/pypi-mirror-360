import asyncio

from pathlib import Path
import time
from typing import Any, Awaitable, Callable
from re_common.v2.baselibrary.tools.concurrency import AsyncTaskPool
from re_common.v2.baselibrary.tools.hdfs_base_processor import HDFSBaseProcessor


class HDFSLineProcessor(HDFSBaseProcessor):
    async def _process_data(self, data, process_func, pool):
        """处理数据并执行处理函数"""
        retry_count = 0
        while retry_count < self.retries:
            try:
                return await process_func(data, pool)  # 成功处理后退出
            except Exception as e:
                retry_count += 1
                print(f"处理数据时发生错误: {e}, 正在重试 {retry_count}/{self.retries}, data: {data}")
                await asyncio.sleep(2**retry_count)
        raise Exception(f"处理数据失败, 达到重试上限, data: {data}")

    async def _process_file(self, hdfs_file_path, process_func):
        """处理单个 gz 文件"""
        start_time = time.perf_counter()
        total_lines = self._count_total_lines(hdfs_file_path)
        processed_lines = 0
        pool = await self._get_pool()
        results = []

        for lines in self._batch_read_gz(hdfs_file_path):
            processing_start_time = time.perf_counter()  # 记录本批处理开始时间

            tasks = [self._process_data(line, process_func, pool) for line in lines]
            results.extend(await AsyncTaskPool(self.concurrency).run(tasks))

            processed_lines += len(lines)

            self._print_progress(hdfs_file_path, processed_lines, total_lines, start_time, processing_start_time)

        if self.result_dir is not None:
            self.client.write(
                self.result_dir.rstrip("/") + f"/{Path(hdfs_file_path).stem}",
                data=self._generate_write_data(results),
                overwrite=True,
                encoding=self.encoding,
            )

        # 最终进度显示
        self._print_final_progress(hdfs_file_path, processed_lines, total_lines, start_time)

    async def map(self, process_func: Callable[[str, Any], Awaitable[Any]]) -> None:
        gz_files = self._list_gz_files()
        await self._run_multi_process(gz_files, process_func)


# async def test_func(line: str, pool):
#     pass


# async def main():
#     await HDFSLineProcessor(
#         "/xx/xx",
#         db_path=Path(__file__).parent / "test.db",
#         concurrency=200,
#         batch_size=1000,
#         pool_factory=get_pool,
#         max_processes=2,
#         result_dir="/xx/xx_res",
#     ).map(test_func)


# if __name__ == "__main__":
#     asyncio.run(main())
