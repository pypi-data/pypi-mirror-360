import asyncio
import gzip
import json
from pathlib import Path
import sqlite3
import time
import os
from io import BytesIO
from typing import Callable, Any, List

from hdfs import InsecureClient


class HDFSDataProcessor:
    def __init__(
        self,
        hdfs_url="http://VIP-DC-MASTER-2:9870",
        hdfs_user="root",
        db_file="processed_files.db",
        batch_size=50,
        retry_limit=3,
    ):
        self.hdfs_url = hdfs_url
        self.hdfs_user = hdfs_user
        self.db_file = db_file
        self.batch_size = batch_size
        self.retry_limit = retry_limit
        self.client = InsecureClient(self.hdfs_url, user=self.hdfs_user)
        self.read_hdfs_fanc = {"all": self.all_read_gz, "batch": self.batch_read_gz}
        self.read_hdfs_model = "all"
        self.init_db()

    def init_db(self):
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
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)",
                (file_path,),
            )
            conn.commit()

    def is_file_processed(self, file_path):
        """检查文件是否已处理"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT file_path FROM processed_files WHERE file_path = ?",
                (file_path,),
            )
            result = cursor.fetchone()
        return result is not None

    def list_gz_files(self, hdfs_dir):
        """列出 HDFS 目录中的所有 gzip 文件"""
        return [f"{hdfs_dir}/{file[0]}" for file in self.client.list(hdfs_dir, status=True) if file[0].endswith(".gz")]

    def count_total_lines(self, gz_file_path: str):
        with self.client.read(gz_file_path) as hdfs_file:
            with gzip.GzipFile(fileobj=hdfs_file) as gz:
                return sum(1 for _ in gz)

    def batch_read_gz(self, gz_file_path: str):
        """分批读取 gz 文件"""
        with self.client.read(gz_file_path) as hdfs_file:
            with gzip.GzipFile(fileobj=hdfs_file) as gz:
                while True:
                    lines = []
                    for _ in range(self.batch_size):
                        try:
                            line = next(gz)
                            if line.strip():  # 移除空行
                                lines.append(line.decode("utf-8"))  # 解码
                        except StopIteration:  # 文件已读完
                            break
                    if not lines:
                        break
                    yield lines

    def all_read_gz(self, gz_file_path: str, encoding="utf-8"):
        """
        读取 HDFS 上的 .gz 文件内容。
        :param hdfs_path: HDFS 文件路径（必须以 .gz 结尾）
        :param encoding: 文件编码格式（默认 utf-8）
        :return: 文件内容
        """
        with self.client.read(gz_file_path) as reader:  # 以二进制模式读取
            compressed_data = reader.read()  # 读取压缩数据
            with gzip.GzipFile(fileobj=BytesIO(compressed_data)) as gz_file:  # 解压缩
                content = gz_file.read().decode(encoding)  # 解码为字符串
                print(f"文件读取成功: {gz_file_path}")
                lines = [i for i in content.split("\n") if i.strip()]
                result = [lines[i : i + self.batch_size] for i in range(0, len(lines), self.batch_size)]
                return result

    async def process_data(self, data, process_func):
        """处理数据并执行处理函数"""
        retry_count = 0
        while retry_count < self.retry_limit:
            try:
                return await process_func(data)  # 成功处理后退出
            except Exception as e:
                retry_count += 1
                print(f"处理数据时发生错误: {e}, 正在重试 {retry_count}/{self.retry_limit}, data: {data}")
                await asyncio.sleep(2**retry_count)
        raise Exception(f"处理数据失败, 达到重试上限, data: {data}")

    async def process_file(self, hdfs_file_path, process_func, write_dir: str):
        """处理单个 gz 文件"""
        total_lines = self.count_total_lines(hdfs_file_path)
        processed_lines = 0
        start_time = time.time()
        results = []
        #   # 这里根据不同的配置选用不同的读取文件的方法
        for lines in self.read_hdfs_fanc[self.read_hdfs_model](hdfs_file_path):
            processing_start_time = time.time()  # 记录本批处理开始时间

            tasks = []
            for line in lines:
                try:
                    data = json.loads(line)
                    tasks.append(self.process_data(data, process_func))
                except json.JSONDecodeError as e:
                    raise Exception(f"解析JSON失败: {e}, 行内容: {line.strip()}")

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

        def generate_write_data(results):
            for res in results:
                yield str(res) + "\n"

        if write_dir is not None:
            self.client.write(
                write_dir.rstrip("/") + f"/{Path(hdfs_file_path).stem}",
                data=generate_write_data(results),
                overwrite=True,
                encoding="utf-8",
            )

        # 最终进度显示
        final_elapsed_time = time.time() - start_time  # 最终已用时间
        print(
            f"文件: {hdfs_file_path} 处理完成 | 总进度: {processed_lines}/{total_lines} 行 | "
            f"总已用时间: {final_elapsed_time:.2f}秒 | "
            f"平均每条处理时间: {(final_elapsed_time * 1000) / processed_lines:.2f}毫秒"
            if processed_lines > 0
            else "处理无数据"
        )

        self.save_processed_file(hdfs_file_path)  # 保存处理过的文件

    async def retry_process_file(self, hdfs_file_path, process_func, write_dir):
        """带重试机制的文件处理"""
        retry_count = 0
        while retry_count < self.retry_limit:
            try:
                await self.process_file(hdfs_file_path, process_func, write_dir)
                return True  # 成功处理后退出
            except Exception as e:
                retry_count += 1
                print(f"处理文件 {hdfs_file_path} 时发生错误: {e}，正在重试 {retry_count}/{self.retry_limit}")
                await asyncio.sleep(2**retry_count)
        print(f"处理文件 {hdfs_file_path} 失败，达到重试上限")
        return False
        # raise

    async def batch_process_file(self, hdfs_dir: str, process_func: Callable[[dict], Any], write_dir: str = None):
        """批量更新所有 gz 文件"""
        gz_files = self.list_gz_files(hdfs_dir)
        all_succeed = True
        for hdfs_file_path in gz_files:
            if self.is_file_processed(hdfs_file_path):
                print(f"跳过已处理文件: {hdfs_file_path}")
                continue  # 如果文件已处理，跳过
            succeed = await self.retry_process_file(hdfs_file_path, process_func, write_dir)  # 处理文件
            if succeed is False:
                all_succeed = False

        if all_succeed:
            # 处理完成后删除数据库文件
            try:
                if os.path.exists(self.db_file):
                    os.remove(self.db_file)
                    print(f"已删除断点重试文件: {self.db_file}")
            except Exception as e:
                print(f"删除断点重试文件失败: {e}")

    async def process_file_bulk(self, hdfs_file_path, process_func):
        """按批次处理单个文件，批量数据传递给处理函数"""
        total_lines = self.count_total_lines(hdfs_file_path)
        processed_lines = 0
        start_time = time.time()

        tasks = []
        # 这里根据不同的配置选用不同的读取文件的方法
        for lines in self.read_hdfs_fanc[self.read_hdfs_model](hdfs_file_path):
            processing_start_time = time.time()  # 记录本批处理开始时间

            batch_data = []
            for line in lines:
                try:
                    data = json.loads(line)
                    batch_data.append(data)
                except json.JSONDecodeError as e:
                    raise Exception(f"解析JSON失败: {e}, 行内容: {line.strip()}")

            # 处理读取到的批次数据
            if batch_data:
                tasks.append(process_func(batch_data))  # 将批次数据传递给处理函数并收集任务
                processed_lines += len(batch_data)  # 更新已处理行数

            # 当积累的任务数量达到 batch_size 时并发处理所有任务
            if len(tasks) >= self.batch_size:
                await asyncio.gather(*tasks)  # 同时处理多个批次

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
            await asyncio.gather(*tasks)  # 处理未达到 batch_size 的剩余任务

        # 最终进度显示
        final_elapsed_time = time.time() - start_time  # 最终已用时间
        print(
            f"文件: {hdfs_file_path} 处理完成 | 总进度: {processed_lines}/{total_lines} 行 | "
            f"总已用时间: {final_elapsed_time:.2f}秒 | "
            f"平均每条处理时间: {(final_elapsed_time * 1000) / processed_lines:.2f}毫秒"
            if processed_lines > 0
            else "处理无数据"
        )

        self.save_processed_file(hdfs_file_path)

    async def retry_process_file_bulk(self, hdfs_file_path, process_func):
        """带重试机制的批量文件处理"""
        retry_count = 0
        while retry_count < self.retry_limit:
            try:
                await self.process_file_bulk(hdfs_file_path, process_func)
                return True  # 成功处理后退出
            except Exception as e:
                retry_count += 1
                print(f"处理文件 {hdfs_file_path} 时发生错误: {e}，正在重试 {retry_count}/{self.retry_limit}")
                await asyncio.sleep(2**retry_count)
        print(f"处理文件 {hdfs_file_path} 失败，达到重试上限")
        return False

    async def batch_process_file_bulk(self, hdfs_dir: str, process_func: Callable[[List[dict]], Any]):
        """批量处理 gz 文件中的数据"""
        gz_files = self.list_gz_files(hdfs_dir)
        all_succeed = True
        for hdfs_file_path in gz_files:
            if self.is_file_processed(hdfs_file_path):
                print(f"跳过已处理文件: {hdfs_file_path}")
                continue  # 跳过已处理文件
            succeed = await self.retry_process_file_bulk(hdfs_file_path, process_func)
            if succeed is False:
                all_succeed = False

        if all_succeed:
            # 处理完成后删除数据库文件
            try:
                if os.path.exists(self.db_file):
                    os.remove(self.db_file)
                    print(f"已删除断点重试文件: {self.db_file}")
            except Exception as e:
                print(f"删除断点重试文件失败: {e}")


# # 使用示例
# async def update_refer(data: dict):
#     ref_id = data["ref_id"]
#     url = f"http://192.168.98.79:8150/v1/fact_refer/update/{ref_id}"
#     update_data = data["update_data"]
#     if not update_data:
#         return
#
#     # 此处为实际处理逻辑
#     await ApiNetUtils.fetch_post(url=url, payload=update_data)
#
#
# if __name__ == "__main__":
#     processor = HDFSDataProcessor()  # 实例化数据处理类
#     asyncio.run(processor.batch_process_file("/user/libaiyun/output/confidence", update_refer))
