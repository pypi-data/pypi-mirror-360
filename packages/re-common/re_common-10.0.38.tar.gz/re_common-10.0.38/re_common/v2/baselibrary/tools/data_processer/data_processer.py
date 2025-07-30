import asyncio
import os
import re
import sqlite3
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import List, Callable, Any

from filelock import FileLock
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_result

from re_common.v2.baselibrary.tools.data_processer.base import BaseFileReader, BaseFileWriter


class DatabaseHandler:
    def __init__(self, db_file="processed_files.db"):
        self.db_file = db_file
        self.lock_file = f"{self.db_file}.lock"
        self._init_db()

    def _init_db(self):
        with FileLock(self.lock_file):
            """初始化 SQLite 数据库"""
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processed_files (
                        file_path TEXT PRIMARY KEY
                    )
                """)
                conn.commit()

    def save_processed_file(self, file_path):
        """保存处理过的文件"""
        with FileLock(self.lock_file):
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)",
                    (file_path,)
                )
                conn.commit()

    def save_processed_files_many(self, file_paths):
        """批量保存处理过的文件路径"""
        if not file_paths:
            return
        with FileLock(self.lock_file):
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    "INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)",
                    ((fp,) for fp in file_paths)
                )
                conn.commit()

    def is_file_processed(self, file_path):
        """检查文件是否已处理"""
        with FileLock(self.lock_file):
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT file_path FROM processed_files WHERE file_path = ?",
                    (file_path,)
                )
                result = cursor.fetchone()
            return result is not None

    def fake_processed_files(self, start_index, end_index, file_list):
        try:
            # 将字符串序号转换为整数
            start = int(start_index)
            end = int(end_index)

            # 验证序号范围
            if start >= end:
                raise ValueError(f"起始序号 {start_index} 必须小于结束序号 {end_index}")

            list_formatted_num = []
            # 为范围内的每个序号生成文件名
            for num in range(start, end):
                # 将序号格式化为5位字符串 (00120, 00121,...)
                formatted_num = f"{num:05d}"
                list_formatted_num.append(formatted_num)

            skip_path_list = []
            skip_formatted_num = []
            for file_path in file_list:
                re_f_num = re.findall(r'(?<!\d)\d{5}(?!\d)', str(Path(file_path).stem))
                if re_f_num:
                    if re_f_num[0] in list_formatted_num:
                        skip_path_list.append(file_path)
                        skip_formatted_num.append(re_f_num[0])

            for item_list in [skip_path_list[i:i + 2000] for i in range(0, len(skip_path_list), 2000)]:
                self.save_processed_files_many(item_list)
                for file_path in item_list:
                    print(f"伪造处理记录: {file_path}")

            no_fil_num = set(list_formatted_num) - set(skip_formatted_num)
            if len(no_fil_num) > 0:
                print(f"没有对应num的文件,伪造失败数量为{len(no_fil_num)},样例:{list(no_fil_num)[:10]}")
            print(f"成功伪造处理记录：序号 {start_index} 到 {end_index}（不含）的文件")

        except ValueError as e:
            print(f"错误: 序号格式无效 - {str(e)}")
        except Exception as e:
            print(f"伪造处理记录时出错: {str(e)}")


class DataProcessor:
    def __init__(
            self,
            reader: BaseFileReader,
            writer: BaseFileWriter = None,
            db_handler: DatabaseHandler = None,
            db_file="processed_files.db",
            batch_size=50,
            retry_limit=3,
    ):
        self.reader = reader
        self.writer = writer
        self.db_file = db_file
        self.batch_size = batch_size
        self.retry_limit = retry_limit
        self.db_handler = db_handler if db_handler else DatabaseHandler(db_file=db_file)

    async def retry_process_data(self, data, process_func):
        """处理数据并执行处理函数"""

        def on_retry(retry_state):
            # 每次抛错进入该函数打印消息
            print(
                f"重试次数: {retry_state.attempt_number}/{self.retry_limit},数据内容: {retry_state.args[0]}\n"
                f"异常信息: {retry_state.outcome.exception()}"
            )

        def on_retry_error(retry_state):
            # 最后抛错后调用
            original_exc = retry_state.outcome.exception()
            raise RuntimeError(
                f"处理数据失败，达到重试上限。data: {retry_state.args[0]}") from original_exc  # 抛出的自定义异常中 保留 __process_func() 里的原始错误堆栈信息（traceback）

        @retry(stop=stop_after_attempt(3),
               wait=wait_exponential(multiplier=1, min=2, max=20),
               before_sleep=on_retry,  # 每次抛错后使用
               retry_error_callback=on_retry_error,  # 如果到最后都没有成功 抛错
               reraise=True)
        async def __process_func(_data):
            return await process_func(_data)

        return await __process_func(data)

    async def process_file(self, hdfs_file_path, process_func, write_dir):
        """处理单个 gz 文件"""
        total_lines = self.reader.count_lines(hdfs_file_path)
        processed_lines = 0
        start_time = time.time()
        results = []
        #   # 这里根据不同的配置选用不同的读取文件的方法
        for lines in self.reader.read_select(hdfs_file_path):
            processing_start_time = time.time()  # 记录本批处理开始时间

            tasks = []
            for line in lines:
                # try:
                #     data = json.loads(line)
                #     tasks.append(self.retry_process_data(data, process_func))
                # except json.JSONDecodeError as e:
                #     raise Exception(f"解析JSON失败: {e}, 行内容: {line.strip()}")
                tasks.append(self.retry_process_data(line, process_func))

            # await AsyncTaskPool(self.batch_size).run(tasks) # AsyncTaskPool 适用于一次提交所有任务, 限制并发数执行
            results.extend(await asyncio.gather(*tasks))

            processed_lines += len(lines)

            elapsed_time = time.time() - start_time  # 已用时间
            processing_time = time.time() - processing_start_time  # 本次处理时间
            avg_processing_time = (
                (elapsed_time * 1000) / processed_lines if processed_lines > 0 else float("inf")
            )  # 平均每条数据的处理时间（毫秒）

            # 估算剩余时间
            remaining_time = (
                ((avg_processing_time / 1000) * (total_lines - processed_lines))
                if processed_lines > 0
                else float("inf")
            )

            # 显示总进度信息
            print(
                f"文件: {hdfs_file_path} 总进度: {processed_lines}/{total_lines} 行 | "
                f"已用时间: {elapsed_time:.2f}秒 | 本次处理时间: {processing_time:.2f}秒 | "
                f"预估剩余时间: {remaining_time:.2f}秒 | 平均每条处理时间: {avg_processing_time:.2f}毫秒"
            )

        if write_dir is not None:
            if not self.writer:
                raise Exception("没有配置写数据的对象")
            write_path = write_dir.rstrip("/") + f"/{Path(hdfs_file_path).stem}"
            self.writer.write_lines([str(item) for item in results], write_path)

        # 最终进度显示
        final_elapsed_time = time.time() - start_time  # 最终已用时间
        print(
            f"文件: {hdfs_file_path} 处理完成 | 总进度: {processed_lines}/{total_lines} 行 | "
            f"总已用时间: {final_elapsed_time:.2f}秒 | "
            f"平均每条处理时间: {(final_elapsed_time * 1000) / processed_lines:.2f}毫秒"
            if processed_lines > 0
            else "处理无数据"
        )

        self.db_handler.save_processed_file(hdfs_file_path)  # 保存处理过的文件

    async def retry_process_file(self, hdfs_file_path, process_func, write_dir):
        """带重试机制的文件处理"""

        def on_retry(retry_state):
            # 每次抛错进入该函数打印消息
            exc = retry_state.outcome.exception()
            tb = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            print(tb)

            print(
                f"处理文件 {retry_state.args[0]} 时发生错误: {exc}，正在重试 {retry_state.attempt_number}/{self.retry_limit}")

        def on_retry_error(retry_state):
            # 最后抛错后调用
            print(f"处理文件 {retry_state.args[0]} 失败，达到重试上限")
            return False

        @retry(stop=stop_after_attempt(3),
               wait=wait_exponential(multiplier=1, min=2, max=20),
               before_sleep=on_retry,  # 每次抛错后使用
               retry_error_callback=on_retry_error,  # 如果最后没成功 返回 False
               reraise=True)
        async def __process_func(_hdfs_file_path, _process_func, _write_dir):
            await self.process_file(_hdfs_file_path, _process_func, _write_dir)
            return True  # 成功处理后退出

        return await __process_func(hdfs_file_path, process_func, write_dir)

    def get_file_list(self, hdfs_dir):
        # 获取所有任务文件
        all_files = self.reader.list_files(hdfs_dir)
        for file_path in all_files:
            yield file_path

    @retry(stop=stop_after_attempt(3),
           wait=wait_random(min=10, max=30),
           retry=retry_if_result(lambda result: not result),  # 如果返回值是 False（失败），则重试 最后会抛出一个默认错误tenacity.RetryError:
           reraise=True)
    async def _batch_process_file(self, hdfs_file_path: str, process_func: Callable[[str], Any],
                                  write_dir: str = None):
        """批量更新所有 gz 文件"""
        # all_succeed = True
        # for hdfs_file_path in self.get_file_list(hdfs_dir):
        #     if self.db_handler.is_file_processed(hdfs_file_path):
        #         print(f"跳过已处理文件: {hdfs_file_path}")
        #         continue  # 如果文件已处理，跳过
        #     succeed = await self.retry_process_file(hdfs_file_path, process_func, write_dir)  # 处理文件
        #     if succeed is False:
        #         all_succeed = False
        #
        # if all_succeed:
        #     # 处理完成后删除数据库文件
        #     try:
        #         if os.path.exists(self.db_file):
        #             os.remove(self.db_file)
        #             print(f"已删除断点重试文件: {self.db_file}")
        #             return True
        #     except Exception as e:
        #         print(f"删除断点重试文件失败: {e}")
        # return False
        if self.db_handler.is_file_processed(hdfs_file_path):
            print(f"跳过已处理文件: {hdfs_file_path}")
            return True  # 如果文件已处理，跳过
        succeed = await self.retry_process_file(hdfs_file_path, process_func, write_dir)  # 处理文件
        return succeed

    async def process_file_bulk(self, hdfs_file_path, process_func, write_dir):
        """按批次处理单个文件，批量数据传递给处理函数"""
        # 获取文件的数据总量
        total_lines = self.reader.count_lines(hdfs_file_path)
        processed_lines = 0
        start_time = time.time()

        results = []
        tasks = []
        # 这里根据不同的配置选用不同的读取文件的方法
        for lines in self.reader.read_select(hdfs_file_path):
            processing_start_time = time.time()  # 记录本批处理开始时间

            # batch_data = []
            # for line in lines:
            #     try:
            #         data = json.loads(line)
            #         batch_data.append(data)
            #     except json.JSONDecodeError as e:
            #         raise Exception(f"解析JSON失败: {e}, 行内容: {line.strip()}")

            # 处理读取到的批次数据
            if lines:
                tasks.append(process_func(lines))  # 将批次数据传递给处理函数并收集任务
                processed_lines += len(lines)  # 更新已处理行数

            # 当积累的任务数量达到 batch_size 时并发处理所有任务
            if len(tasks) >= self.batch_size:
                results.extend(await asyncio.gather(*tasks))
                elapsed_time = time.time() - start_time  # 已用时间
                processing_time = time.time() - processing_start_time  # 本次处理时间
                avg_processing_time = (
                    (elapsed_time * 1000) / processed_lines if processed_lines > 0 else float("inf")
                )  # 平均每条数据的处理时间（毫秒）

                # 估算剩余时间
                remaining_time = (
                    ((avg_processing_time / 1000) * (total_lines - processed_lines))
                    if processed_lines > 0
                    else float("inf")
                )

                # 显示总进度信息
                print(
                    f"文件: {hdfs_file_path} 总进度: {processed_lines}/{total_lines} 行 | "
                    f"已用时间: {elapsed_time:.2f}秒 | 本次处理时间: {processing_time:.2f}秒 | "
                    f"预估剩余时间: {remaining_time:.2f}秒 | 平均每条处理时间: {avg_processing_time:.2f}毫秒"
                )

                # 清空任务列表，准备下一批处理
                tasks.clear()
            # 处理剩余的任务
        if tasks:
            results.extend(await asyncio.gather(*tasks))  # 处理未达到 batch_size 的剩余任务

        if write_dir is not None:
            if not self.writer:
                raise Exception("没有配置写数据的对象")
            write_path = write_dir.rstrip("/") + f"/{Path(hdfs_file_path).stem}"
            self.writer.write_lines([str(item) for items in results for item in items], write_path)

        # 最终进度显示
        final_elapsed_time = time.time() - start_time  # 最终已用时间
        print(
            f"文件: {hdfs_file_path} 处理完成 | 总进度: {processed_lines}/{total_lines} 行 | "
            f"总已用时间: {final_elapsed_time:.2f}秒 | "
            f"平均每条处理时间: {(final_elapsed_time * 1000) / processed_lines:.2f}毫秒"
            if processed_lines > 0
            else "处理无数据"
        )

        self.db_handler.save_processed_file(hdfs_file_path)

    async def retry_process_file_bulk(self, hdfs_file_path, process_func, write_dir):
        """带重试机制的批量文件处理"""

        def on_retry(retry_state):
            # 每次抛错进入该函数打印消息
            exc = retry_state.outcome.exception()
            tb = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            print(tb)
            print(
                f"处理文件 {retry_state.args[0]} 时发生错误: {exc}，正在重试 {retry_state.attempt_number}/{self.retry_limit}")

        def on_retry_error(retry_state):
            # 最后抛错后调用
            print(f"处理文件 {retry_state.args[0]} 失败，达到重试上限")
            return False

        @retry(stop=stop_after_attempt(3),
               wait=wait_exponential(multiplier=1, min=2, max=20),
               before_sleep=on_retry,  # 每次抛错后使用
               retry_error_callback=on_retry_error,  # 如果最后没成功 返回 False
               reraise=True)
        async def __process_func(_hdfs_file_path, _process_func, write_dir):
            await self.process_file_bulk(_hdfs_file_path, _process_func, write_dir)
            return True  # 成功处理后退出

        return await __process_func(hdfs_file_path, process_func, write_dir)

    async def batch_process_file(self, hdfs_dir: str, process_func: Callable[[List[str]], Any] | Callable[[str], Any],
                                 write_dir: str = None, is_bulk: bool = False):
        all_succeed = True
        for hdfs_file_path in self.get_file_list(hdfs_dir):
            if is_bulk:
                succeed = await self._batch_process_file_bulk(hdfs_file_path, process_func, write_dir)
            else:
                succeed = await self._batch_process_file(hdfs_file_path, process_func, write_dir)
            if succeed is False:
                all_succeed = False
        if all_succeed:
            # 处理完成后删除数据库文件
            try:
                if os.path.exists(self.db_file):
                    os.remove(self.db_file)
                    print(f"已删除断点重试文件: {self.db_file}")
                    return True
            except Exception as e:
                print(f"删除断点重试文件失败: {e}")
        return False

    @retry(stop=stop_after_attempt(3),
           wait=wait_random(min=10, max=30),
           retry=retry_if_result(lambda result: not result),  # 如果返回值是 False（失败），则重试 最后会抛出一个默认错误tenacity.RetryError:
           reraise=True)
    async def _batch_process_file_bulk(self, hdfs_file_path: str, process_func: Callable[[List[str]], Any],
                                       write_dir: str = None):
        """批量处理 gz 文件中的数据"""
        # 获取所有文件
        # all_succeed = True
        # for hdfs_file_path in self.get_file_list(hdfs_dir):
        #     # 查看是否跳过文件
        #     if self.db_handler.is_file_processed(hdfs_file_path):
        #         print(f"跳过已处理文件: {hdfs_file_path}")
        #         continue  # 跳过已处理文件
        #     # 开始批量处理文件
        #     succeed = await self.retry_process_file_bulk(hdfs_file_path, process_func, write_dir)
        #     if succeed is False:
        #         all_succeed = False
        #
        # if all_succeed:
        #     # 处理完成后删除数据库文件
        #     try:
        #         if os.path.exists(self.db_file):
        #             os.remove(self.db_file)
        #             print(f"已删除断点重试文件: {self.db_file}")
        #             return True
        #     except Exception as e:
        #         print(f"删除断点重试文件失败: {e}")
        # return False
        # 查看是否跳过文件
        if self.db_handler.is_file_processed(hdfs_file_path):
            print(f"跳过已处理文件: {hdfs_file_path}")
            return True  # 跳过已处理文件
        # 开始批量处理文件
        succeed = await self.retry_process_file_bulk(hdfs_file_path, process_func, write_dir)
        return succeed


# 全局变量，每个进程独立持有
_processor: DataProcessor | None = None
_process_func: Callable[[List[str]], Any] | Callable[[str], Any] | None = None
_process_args: dict


def get_data_processor_func(process_args):
    _func_reader = process_args["reader_func"]
    _reader_args = process_args["reader_kwargs"]
    reader = _func_reader(**_reader_args)
    writer = None
    if process_args["is_writer"]:
        _func_writer = process_args["writer_func"]
        _writer_args = process_args["writer_kwargs"]
        writer = _func_writer(**_writer_args)

    data_kwargs = {
        "reader": reader,
        "writer": writer,
        "db_file": process_args["db_file"]
    }
    if process_args.get("batch_size"):
        data_kwargs["batch_size"] = process_args["batch_size"]
    if process_args.get("retry_limit"):
        data_kwargs["retry_limit"] = process_args["retry_limit"]

    return DataProcessor(**data_kwargs)


def init_worker(process_func, process_args):
    global _processor, _process_func, _process_args
    _processor = get_data_processor_func(process_args)
    _process_func = process_func
    _process_args = process_args

    _init_func = _process_args.get("init_work", None)
    if _init_func:
        _init_func()

    _async_init_work = _process_args.get("async_init_work", None)
    if _init_func:
        asyncio.run(_async_init_work())


def worker(path_file):
    if _process_args["is_bulk"]:
        return asyncio.run(_processor._batch_process_file_bulk(path_file, _process_func, _process_args["write_dir"]))
    else:
        return asyncio.run(_processor._batch_process_file(path_file, _process_func, _process_args["write_dir"]))


def run_worker_many(hdfs_dir: str, process_func: Callable[[List[str]], Any] | Callable[[str], Any],
                    data_process_args: dict, max_workers=4):
    processor = get_data_processor_func(data_process_args)
    all_file = list(processor.get_file_list(hdfs_dir))
    with ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=init_worker,
            initargs=(process_func, data_process_args)
    ) as executor:
        # 提交任务并等待结果
        results = executor.map(worker, all_file)
    # 输出结果
    for result in results:
        if result:
            print(result)
