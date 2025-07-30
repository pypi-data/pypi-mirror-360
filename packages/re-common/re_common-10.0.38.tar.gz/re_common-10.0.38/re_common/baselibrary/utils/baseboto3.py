import boto3
import botocore
from boto3.session import Session

# boto3 该开发工具包由两个关键的 Python 包组成：
# Botocore（提供在 Python 开发工具包和 AWS CLI 之间共享的低级功能的库）
# 和 Boto3（实现 Python 开发工具包本身的包）


"""
aws_access_key_id = 'minioa'
aws_secret_access_key = 'minio123'
endpoint_url = 'http://192.168.31.164:9000'
bbt = BaseBoto3(aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url=endpoint_url)
bbt.conn_session()
bbt.set_is_low_level(False)
bbt.get_client()
print("**********************")
print(bbt.delete_buckets("test1"))
# bbt.set_is_low_level(False)
# bbt.get_client()
# print("**********************")
# print(bbt.create_buckets("create2"))
"""


class BaseBoto3(object):

    def __init__(self, aws_access_key_id="", aws_secret_access_key="", endpoint_url=""):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.session = None
        self.client = None
        self.is_low_level = False
        self.bucket = None

    def set_is_low_level(self, is_low_level):
        self.is_low_level = is_low_level
        return self

    def set_aws_access_key_id(self, aws_access_key_id):
        self.aws_access_key_id = aws_access_key_id
        return self

    def set_aws_secret_access_key(self, aws_secret_access_key):
        self.aws_secret_access_key = aws_secret_access_key
        return self

    def set_endpoint_url(self, endpoint_url):
        self.endpoint_url = endpoint_url
        return self

    def conn_session(self):
        self.session = Session(aws_access_key_id=self.aws_access_key_id,
                               aws_secret_access_key=self.aws_secret_access_key)
        return self.session

    def get_client(self):
        assert self.session is not None
        if self.is_low_level:
            # 根据名称创建低级服务客户端
            # botocore.client.S3
            self.client = self.session.client('s3', endpoint_url=self.endpoint_url)
            print(type(self.client))
        else:
            # boto3.resources.factory.s3.ServiceResource
            # 按名称创建资源服务客户端
            self.client = self.session.resource('s3', endpoint_url=self.endpoint_url)
            print(type(self.client))
        return self

    def get_all_buckets(self):
        """
        获取所有的桶信息
        :return:
        """
        if self.is_low_level is False:
            return self.client.buckets.all()
        else:
            return self.client.list_buckets()

    def create_buckets(self, buckets_name):
        """

        :param buckets_name:
        :return:
        如果get_client 使用 client 返回
        {'ResponseMetadata': {'RequestId': '16BC90EED4A433C4', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'accept-ranges': 'bytes', 'content-length': '0', 'content-security-policy': 'block-all-mixed-content', 'location': '/create1', 'server': 'MinIO', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'vary': 'Origin, Accept-Encoding', 'x-amz-request-id': '16BC90EED4A433C4', 'x-content-type-options': 'nosniff', 'x-xss-protection': '1; mode=block', 'date': 'Wed, 01 Dec 2021 07:28:39 GMT'}, 'RetryAttempts': 0}, 'Location': '/create1'}
        如果resource 使用 client 返回
        s3.Bucket(name='create2')
        """
        assert buckets_name.find("_") == -1, "新建一个bucket桶(bucket name 中不能有_下划线)"
        # 新建一个bucket桶(bucket name 中不能有_下划线)
        return self.client.create_bucket(Bucket=buckets_name)

    def delete_buckets(self, bucket_name):
        """
        删除桶 删除bucket(只能删除空的bucket)
        :return:
        """
        if self.is_low_level is False:
            bucket = self.client.Bucket(bucket_name)
            response = bucket.delete()
        else:
            response = self.client.delete_bucket(Bucket=bucket_name)
        return response

    def get_bucket(self, bucket_name):
        """
        获取 bucket 对象
        :param bucket_name:
        :return:
        """
        if self.is_low_level is False:
            self.bucket = self.client.Bucket(bucket_name)
            return self.bucket
        else:
            raise Exception("无实现方法")

    def get_all_obs_filter(self, Prefix):
        """
        Prefix 为匹配模式
        例：列出前缀为 haha 的文件
        Prefix='haha'
        :param Prefix:
        :return: 可以调用 obj.key
        """
        if not self.is_low_level:
            for obj in self.bucket.objects.filter(Prefix=Prefix):
                yield obj
        else:
            raise Exception("请设置 is_low_level 为 False")

    def get_object(self, bucket_name):
        """
        会返回包括目录在内的所有对象
        :param bucket_name:
        :return:
        """
        if self.is_low_level is False:
            bucket = self.client.Bucket(bucket_name)
            # boto3.resources.collection.s3.Bucket.objectsCollection
            all_obj = bucket.objects.all()
            return all_obj
            # for obj in bucket.objects.all():
            #     print('obj name:%s' % obj.key)
        else:
            return self.client.list_objects(Bucket=bucket_name)

    def upload_file(self, local_file, bucket_name, key):
        """
        # key 桶中的位置 test1/test.pdf
        :param local_file:  本地文件路径
        :param bucket_name: 桶名
        :param key: 远程文件路径
        :return:
        """

        if self.is_low_level is False:
            self.client.Bucket(bucket_name).upload_file(local_file, key)
        else:
            self.client.upload_file(local_file, bucket_name, key)

    def upload_fileobj(self, fileobj, bucket_name, key):
        # fileobj 字节流
        if self.is_low_level is False:
            self.client.Bucket(bucket_name).upload_fileobj(fileobj, key)
        else:
            self.client.upload_fileobj(fileobj, bucket_name, key)

    def download_file(self, local_file, bucket_name, key):
        if self.is_low_level is False:
            self.client.Bucket(bucket_name).download_file(key, local_file)
        else:
            self.client.download_file(bucket_name, key, local_file)

    def download_fileobj(self, fileobj, bucket_name, key):
        if self.is_low_level is False:
            self.client.Bucket(bucket_name).download_fileobj(key, fileobj)
        else:
            self.client.download_fileobj(bucket_name, key, fileobj)

    def check_exist(self, bucket_name, key):
        """
         if self.is_low_level:
            {'ResponseMetadata': {'RequestId': '17E6A65A2B299D3B', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'accept-ranges': 'bytes', 'content-length': '117', 'content-security-policy': 'block-all-mixed-content', 'content-type': 'binary/octet-stream', 'etag': '"2237a934f176003e41abf3d733291079"', 'last-modified': 'Thu, 25 Jul 2024 05:49:43 GMT', 'server': 'MinIO', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'vary': 'Origin, Accept-Encoding', 'x-amz-request-id': '17E6A65A2B299D3B', 'x-content-type-options': 'nosniff', 'x-xss-protection': '1; mode=block', 'date': 'Mon, 29 Jul 2024 09:53:33 GMT'}, 'RetryAttempts': 0}, 'AcceptRanges': 'bytes', 'LastModified': datetime.datetime(2024, 7, 25, 5, 49, 43, tzinfo=tzutc()), 'ContentLength': 117, 'ETag': '"2237a934f176003e41abf3d733291079"', 'ContentType': 'binary/octet-stream', 'Metadata': {}}
        判定文件是否存在，
        :param bucket_name: 桶名
        :param key:  文件key
        :return:
        """

        if self.is_low_level:
            try:
                obj_info = self.client.head_object(
                    Bucket=bucket_name,
                    Key=key
                )
                return obj_info
            except:
                return None
        else:
            # 获取指定存储桶
            bucket = self.client.Bucket(bucket_name)
            # 检查 key 是否存在
            objs = list(bucket.objects.filter(Prefix=key))
            if len(objs) > 0 and objs[0].key == key:
                # [s3.ObjectSummary(bucket_name='crawl.dc.cqvip.com', key='foreign/organ/parsel_organ_log.txt')]
                return objs[0]
            else:
                return None

    def get_prefix_obj(self, bucket, prefix, delimiter):
        """
        Bucket="crawl.dc.cqvip.com",
         Prefix="foreign/organ/ei/",
         Delimiter='/'

        Returns:

        """
        if self.is_low_level:
            # for common_prefix in response.get('CommonPrefixes', []): 获取子目录
            return self.client.list_objects_v2(Bucket=bucket,
                                               Prefix=prefix,
                                               Delimiter=delimiter)  # 设置 Delimiter='/' 可以确保只列出目录而不是所有对象。
        else:
            # 该方法只能列出文件 没办法列出目录
            # bucket_resource = self.client.Bucket(bucket)
            # objects = bucket_resource.objects.filter(Prefix=prefix, Delimiter=delimiter)
            # return list(objects)

            bucket_resource = self.client.Bucket(bucket)
            return bucket_resource.meta.client.list_objects_v2(Bucket=bucket,
                                                               Prefix=prefix,
                                                               Delimiter=delimiter)

    def get_object_value(self, bucket_name, file_key, encoding='utf-8'):
        """
        读取文本数据
        Returns:

        """
        if self.is_low_level:
            obj = self.client.get_object(Bucket=bucket_name, Key=file_key)
            body = obj['Body'].read().decode(encoding)
            return body
        else:
            bucket_resource = self.client.Bucket(bucket_name)
            obj = bucket_resource.Object(file_key)
            body = obj.get()['Body'].read().decode(encoding)
            return body

    def put_object(self, bucket_name, key, body):
        """
        直接写内容到文件
        Args:
            bucket_name:
            key:
            body: 需要 编码 .encode('utf-8')

        Returns:

        """
        if self.is_low_level:
            self.client.put_object(Bucket=bucket_name,
                                   Key=key,
                                   Body=body)
        else:
            # 获取 Bucket 对象
            bucket_resource = self.client.Bucket(bucket_name)

            # 将内容写入文件
            bucket_resource.put_object(Key=key, Body=body)


bb = BaseBoto3(aws_access_key_id="UM51J2G5ZG0FE5CCERB9",
               aws_secret_access_key="u+OEmhE2fahF2L+oXB+HXe8IJs22Lo38icvlF+Yq",
               endpoint_url="http://192.168.31.135:9000"
               )
bb.conn_session()
bb.set_is_low_level(False)
bb.get_client()

result = bb.check_exist("crawl.dc.cqvip.com",
                        "foreign/organ/parsel_organ_log.txt")

print(result)
