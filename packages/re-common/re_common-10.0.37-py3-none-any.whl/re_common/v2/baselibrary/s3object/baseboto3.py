from boto3.session import Session


class BaseBoto3(object):

    def __init__(self, aws_access_key_id="", aws_secret_access_key="", endpoint_url=""):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.session = None
        self.client = None
        if self.aws_access_key_id and self.aws_secret_access_key and self.endpoint_url:
            self.conn_session()
            self.get_client()

    def set_key(self, aws_access_key_id, aws_secret_access_key, endpoint_url):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        return self

    def conn_session(self):
        assert self.aws_access_key_id not in (None, '')
        assert self.aws_secret_access_key not in (None, '')
        self.session = Session(aws_access_key_id=self.aws_access_key_id,
                               aws_secret_access_key=self.aws_secret_access_key)
        return self.session

    def get_client(self):
        assert self.session is not None
        self.client = self.session.client('s3', endpoint_url=self.endpoint_url)
        return self

    def get_all_buckets(self):
        """
        获取所有的桶信息
        :return:
        """
        return self.client.list_buckets()

    def create_buckets(self, buckets_name):
        """
         如果get_client 使用 client 返回
        {'ResponseMetadata': {'RequestId': '16BC90EED4A433C4', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'accept-ranges': 'bytes', 'content-length': '0', 'content-security-policy': 'block-all-mixed-content', 'location': '/create1', 'server': 'MinIO', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'vary': 'Origin, Accept-Encoding', 'x-amz-request-id': '16BC90EED4A433C4', 'x-content-type-options': 'nosniff', 'x-xss-protection': '1; mode=block', 'date': 'Wed, 01 Dec 2021 07:28:39 GMT'}, 'RetryAttempts': 0}, 'Location': '/create1'}
        """
        assert buckets_name.find("_") == -1, "新建一个bucket桶(bucket name 中不能有_下划线)"
        # 新建一个bucket桶(bucket name 中不能有_下划线)
        return self.client.create_bucket(Bucket=buckets_name)

    def delete_buckets(self, bucket_name):
        """
        删除桶 删除bucket(只能删除空的bucket)
        :return:
        """
        response = self.client.delete_bucket(Bucket=bucket_name)
        return response

    def get_bucket(self, bucket_name):
        raise Exception("无实现方法")

    def get_all_objs(self, bucket_name, prefix=None, continuation_token=None):
        """

        continuation_token: 如果超过1000 需要传第一次获取结果中的 continuation_token

        response 的结构
        {'ResponseMetadata': {'RequestId': '1818F447C1E7BA3B', 'HostId': '', 'HTTPStatusCode': 200,
        'HTTPHeaders': {'accept-ranges': 'bytes', 'content-length': '3182', 'content-security-policy': 'block-all-mixed-content', 'content-type': 'application/xml',
        'server': 'MinIO', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'vary': 'Origin, Accept-Encoding', 'x-amz-request-id': '1818F447C1E7BA3B',
         'x-content-type-options': 'nosniff', 'x-xss-protection': '1; mode=block', 'date': 'Thu, 09 Jan 2025 07:04:05 GMT'}, 'RetryAttempts': 0},
         'IsTruncated': False, 'Contents':
         [
         {'Key': 'zt_file/zt类型样例数据/11_part-00000.gz', 'LastModified': datetime.datetime(2024, 4, 28, 2, 56, 59, 716000, tzinfo=tzutc()), 'ETag': '"e0d635f171bce6a67ad72265e5f9137d-2"',
          'Size': 18164139, 'StorageClass': 'STANDARD', 'Owner': {'DisplayName': 'minio', 'ID': '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4'}},
        {'Key': 'zt_file/zt类型样例数据/12_part-00000.gz', 'LastModified': datetime.datetime(2024, 4, 28, 2, 56, 57, 70000, tzinfo=tzutc()), 'ETag': '"f238fe9973a2bc0d3e1562c2938ce897-9"',
        'Size': 93710911, 'StorageClass': 'STANDARD', 'Owner': {'DisplayName': 'minio', 'ID': '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4'}},
         ],
         'Name': 'crawl.dc.cqvip.com', 'Prefix': 'zt_file/zt类型样例数据', 'Delimiter': '',
         'MaxKeys': 1000, 'EncodingType': 'url', 'KeyCount': 7}

        """
        if continuation_token:
            # 获取桶中以特定前缀开头的所有对象
            response = self.client.list_objects_v2(Bucket=bucket_name,
                                                   Prefix=prefix,
                                                   ContinuationToken=continuation_token)
        else:
            # 获取桶中以特定前缀开头的所有对象
            response = self.client.list_objects_v2(Bucket=bucket_name,
                                                   Prefix=prefix)
        object_list = []
        # 检查是否有对象存在
        if 'Contents' in response:
            object_list = [obj['Key'] for obj in response['Contents']]

        continuation_token = None
        # 检查是否有更多对象
        if response.get('IsTruncated'):  # 如果返回结果被截断，说明有更多对象
            continuation_token = response.get('NextContinuationToken')

        return object_list, continuation_token

    def list_prefixes(self, bucket_name, prefix=None, Delimiter="/", continuation_token=None):
        """
        获取目录下一层的目录
        prefix: 注意 这个要以 Delimiter 结尾 比如 Delimiter="/" 那么 prefix="a/"
        continuation_token: 如果超过1000 需要传第一次获取结果中的 continuation_token
        return:  ['a/b/', 'a/c/'] 注意 反回的 结果带有prefix 只能返回目录 不能返回文件
        """
        if continuation_token:
            # 获取桶中以特定前缀开头的所有对象
            response = self.client.list_objects_v2(Bucket=bucket_name,
                                                   Prefix=prefix,
                                                   Delimiter=Delimiter,  # 使用斜杠分隔符模拟目录结构
                                                   ContinuationToken=continuation_token)
        else:
            # 获取桶中以特定前缀开头的所有对象
            response = self.client.list_objects_v2(Bucket=bucket_name,
                                                   Delimiter=Delimiter,  # 使用斜杠分隔符模拟目录结构
                                                   Prefix=prefix)
        object_list = []
        # 检查是否有对象存在
        if 'Contents' in response:
            object_list = [obj['Key'] for obj in response['Contents']]

        Prefix_list = []
        # 检查是否有目录存在
        if 'CommonPrefixes' in response:
            Prefix_list = [obj['Prefix'] for obj in response['CommonPrefixes']]

        continuation_token = None
        # 检查是否有更多对象
        if response.get('IsTruncated'):  # 如果返回结果被截断，说明有更多对象
            continuation_token = response.get('NextContinuationToken')

        return object_list, Prefix_list, continuation_token

    def get_object_value(self, bucket_name, file_key, encoding='utf-8'):
        """
        读取文本数据
        Returns:
        """
        obj = self.client.get_object(Bucket=bucket_name, Key=file_key)
        body = obj['Body'].read().decode(encoding)
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
        self.client.put_object(Bucket=bucket_name,
                               Key=key,
                               Body=body)

    def download_file(self, bucket_name, key, local_file):
        """
        return: None
        """
        result = self.client.download_file(bucket_name, key, local_file)
        return result

    def upload_file(self, bucket_name, key, local_file):
        """
        # key 桶中的位置 test1/test.pdf
        :param local_file:  本地文件路径
        :param bucket_name: 桶名
        :param key: 远程文件路径
        :return:
        """
        self.client.upload_file(local_file, bucket_name, key)

    def download_fileobj(self, bucket_name, key, fileobj):
        """
        return: None
        """
        result = self.client.download_fileobj(bucket_name, key, fileobj)
        return result

    def upload_fileobj(self, bucket_name, key, fileobj):
        # fileobj 字节流
        self.client.upload_fileobj(fileobj, bucket_name, key)

    def check_exist_or_file_info(self, bucket_name, key):
        """
        检查文件是否存在且能获取文件info
        {'ResponseMetadata': {'RequestId': '17E6A65A2B299D3B', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders':
         {'accept-ranges': 'bytes', 'content-length': '117', 'content-security-policy': 'block-all-mixed-content', 'content-type': 'binary/octet-stream',
         'etag': '"2237a934f176003e41abf3d733291079"', 'last-modified': 'Thu, 25 Jul 2024 05:49:43 GMT', 'server': 'MinIO',
         'strict-transport-security': 'max-age=31536000; includeSubDomains', 'vary': 'Origin, Accept-Encoding', 'x-amz-request-id': '17E6A65A2B299D3B',
          'x-content-type-options': 'nosniff', 'x-xss-protection': '1; mode=block', 'date': 'Mon, 29 Jul 2024 09:53:33 GMT'}, 'RetryAttempts': 0},
          'AcceptRanges': 'bytes', 'LastModified': datetime.datetime(2024, 7, 25, 5, 49, 43, tzinfo=tzutc()), 'ContentLength': 117, 'ETag': '"2237a934f176003e41abf3d733291079"',
           'ContentType': 'binary/octet-stream', 'Metadata': {}}
        """
        try:
            obj_info = self.client.head_object(
                Bucket=bucket_name,
                Key=key
            )
            return obj_info
        except:
            return None

    def get_prefix_count(self, bucket_name, obj_count, prefix, continuation_token=None):
        """
        统计 某个目录的文件数据量，由于需要每个目录获取一次 性能很慢
        """
        for index in range(10000):
            obj_list, dir_list, token = self.list_prefixes(bucket_name=bucket_name,
                                                           prefix=prefix,
                                                           continuation_token=continuation_token)

            obj_count = obj_count + len(obj_list)
            for dir_sub in dir_list:
                obj_count = self.get_prefix_count(bucket_name, obj_count, dir_sub)

            if token:
                continuation_token = token
            else:
                break

        if index > 10000 - 5:
            raise Exception("循环耗尽，请检查逻辑正确性")

        return obj_count
