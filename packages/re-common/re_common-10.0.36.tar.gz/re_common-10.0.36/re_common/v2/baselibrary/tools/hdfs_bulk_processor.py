from pathlib import Path
import time
from typing import Any, Awaitable, Callable, List
from re_common.v2.baselibrary.tools.concurrency import AsyncTaskPool
from re_common.v2.baselibrary.tools.hdfs_base_processor import HDFSBaseProcessor


class HDFSBulkProcessor(HDFSBaseProcessor):
    def _flat_map(self, results):
        # return itertools.chain.from_iterable(chunked_results)
        for res in results:
            if isinstance(res, list):
                yield from res
            else:
                yield res

    async def _process_file(self, hdfs_file_path, process_func):
        start_time = time.perf_counter()
        total_lines = self._count_total_lines(hdfs_file_path)
        processed_lines = 0
        pool = await self._get_pool()

        tasks = []
        for lines in self._batch_read_gz(hdfs_file_path):
            # 处理读取到的批次数据
            if lines:
                tasks.append(process_func(lines, pool))  # 将批次数据传递给处理函数并收集任务
                processed_lines += len(lines)  # 更新已处理行数
        results = await AsyncTaskPool(self.concurrency).run(tasks)

        if self.result_dir is not None:
            self.client.write(
                self.result_dir.rstrip("/") + f"/{Path(hdfs_file_path).stem}",
                data=self._generate_write_data(self._flat_map(results)),
                overwrite=True,
                encoding=self.encoding,
            )

        # 最终进度显示
        self._print_final_progress(hdfs_file_path, processed_lines, total_lines, start_time)

    async def map(self, process_func: Callable[[List[str], Any], Awaitable[Any]]) -> None:
        gz_files = self._list_gz_files()
        await self._run_multi_process(gz_files, process_func)


# async def test_func(lines: List[str], pool):
#     pass


# async def main():
#     processor = HDFSBulkProcessor(
#         "/xx/xx",
#         db_path=Path(__file__).parent / "test_bulk.db",
#         concurrency=200,
#         batch_size=1000,
#         pool_factory=get_pool,
#         max_processes=2,
#         result_dir="/xx/xx_res",
#     )
#     # processor.tracker.mark_many_processed(f"/xx/xx/part-{num:05d}.gz" for num in range(0, 6000))

#     await processor.map(test_func)


# if __name__ == "__main__":
#     asyncio.run(main())
