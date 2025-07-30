import gzip
from io import BytesIO

from hdfs import InsecureClient


class HDFSUtils(object):
    """
    HDFS 工具类，封装常见的 HDFS 操作。

    InsecureClient: 缺陷 写大文件数据时无法写入不报错
    """

    def __init__(self, hdfs_url, hdfs_user):
        """
        初始化 HDFS 客户端。
        :param hdfs_url: HDFS 的 URL，例如 "http://namenode:50070"
        :param hdfs_user: HDFS 用户名
        """
        self.hdfs_url = hdfs_url
        self.hdfs_user = hdfs_user
        self.client = InsecureClient(hdfs_url, user=hdfs_user)

    def upload_file(self, local_path, hdfs_path, overwrite=False):
        """
        将本地文件上传到 HDFS。
        :param local_path: 本地文件路径
        :param hdfs_path: HDFS 文件路径
        :param overwrite: 是否覆盖已存在的文件
        :return: None
        """
        self.client.upload(hdfs_path, local_path, overwrite=overwrite)
        print(f"文件上传成功: {local_path} -> {hdfs_path}")

    def download_file(self, hdfs_path, local_path, overwrite=False):
        """
        从 HDFS 下载文件到本地。
        :param hdfs_path: HDFS 文件路径
        :param local_path: 本地文件路径
        :param overwrite: 是否覆盖已存在的文件
        :return: None
        """
        self.client.download(hdfs_path, local_path, overwrite=overwrite)
        print(f"文件下载成功: {hdfs_path} -> {local_path}")

    def delete_file(self, hdfs_path, recursive=False):
        """
        删除 HDFS 上的文件或目录。
        :param hdfs_path: HDFS 文件或目录路径
        :param recursive: 是否递归删除目录
        :return: None
        """
        self.client.delete(hdfs_path, recursive=recursive)
        print(f"文件/目录删除成功: {hdfs_path}")

    def create_directory(self, hdfs_path):
        """
        在 HDFS 上创建目录。
        :param hdfs_path: HDFS 目录路径
        :return: None
        """
        self.client.makedirs(hdfs_path)
        print(f"目录创建成功: {hdfs_path}")

    def list_files(self, hdfs_path):
        """
        列出 HDFS 目录下的文件和子目录。
        :param hdfs_path: HDFS 目录路径
        :return: 文件/目录列表
        """
        files = self.client.list(hdfs_path)
        return files

    def read_file(self, hdfs_path):
        """
        读取 HDFS 文件内容。
        :param hdfs_path: HDFS 文件路径
        :return: 文件内容
        """
        with self.client.read(hdfs_path) as reader:
            content = reader.read()
            print(f"文件读取成功: {hdfs_path}")
            return content

    def read_gz_file(self, hdfs_path, encoding='utf-8'):
        """
        读取 HDFS 上的 .gz 文件内容。
        :param hdfs_path: HDFS 文件路径（必须以 .gz 结尾）
        :param encoding: 文件编码格式（默认 utf-8）
        :return: 文件内容
        """
        with self.client.read(hdfs_path) as reader:  # 以二进制模式读取
            compressed_data = reader.read()  # 读取压缩数据
            with gzip.GzipFile(fileobj=BytesIO(compressed_data)) as gz_file:  # 解压缩
                content = gz_file.read().decode(encoding)  # 解码为字符串
                print(f"文件读取成功: {hdfs_path}")
                return content

    def write_file(self, hdfs_path, content, overwrite=False, encoding='utf-8'):
        """
        向 HDFS 文件写入内容。
        :param hdfs_path: HDFS 文件路径
        :param content: 要写入的内容
        :param overwrite: 是否覆盖已存在的文件
        :param encoding: 文件编码格式
        :return: None
        """
        with self.client.write(hdfs_path, overwrite=overwrite, encoding=encoding) as writer:
            writer.write(content)
            print(f"文件写入成功: {hdfs_path}")

    def write_file_kwargs(self, hdfs_path, content, **kwargs):
        """
        向 HDFS 文件写入内容
        自定义参数实现更大的灵活性
        """
        with self.client.write(hdfs_path, **kwargs) as writer:
            writer.write(content)
            print(f"文件写入成功: {hdfs_path}")

    def safe_append_hdfs(self, hdfs_path, content):
        """
        更安全的追加写入方式，显式检查文件是否存在

        :param content: 要写入的内容
        :param hdfs_path: HDFS文件路径
        """
        try:
            # 检查文件是否存在
            file_exists = self.client.status(hdfs_path, strict=False) is not None

            if not file_exists:
                print(f"文件 {hdfs_path} 不存在，将创建新文件")
                # 第一次写入不使用append模式
                with self.client.write(hdfs_path, encoding='utf-8') as writer:
                    writer.write(content)
            else:
                # 追加模式写入
                with self.client.write(hdfs_path, encoding='utf-8', append=True) as writer:
                    writer.write(content)

        except Exception as e:
            print(f"文件操作失败: {str(e)}")
            raise

    def file_exists(self, hdfs_path):
        """
        检查 HDFS 文件或目录是否存在。
        :param hdfs_path: HDFS 文件或目录路径
        :return: 是否存在
        """
        status = self.client.status(hdfs_path, strict=False)
        return status is not None

    def rename_file(self, hdfs_src_path, hdfs_dst_path):
        """
        重命名或移动 HDFS 文件/目录。
        :param hdfs_src_path: 源路径
        :param hdfs_dst_path: 目标路径
        :return: None
        """
        self.client.rename(hdfs_src_path, hdfs_dst_path)
        print(f"文件/目录重命名成功: {hdfs_src_path} -> {hdfs_dst_path}")
