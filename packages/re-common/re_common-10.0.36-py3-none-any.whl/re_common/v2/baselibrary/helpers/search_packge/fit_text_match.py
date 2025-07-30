import gzip
import io
import multiprocessing
import os
import time

import jieba
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


def create_gzip_joblib(obj):
    temp_io = io.BytesIO()
    with gzip.GzipFile(fileobj=temp_io, mode='wb') as f:
        joblib.dump(obj, f)
    temp_io.seek(0)
    return temp_io


def get_gzip_joblib(temp_io):
    with gzip.GzipFile(fileobj=temp_io, mode='rb') as f:
        loaded_obj = joblib.load(f)
    return loaded_obj


class JiebaTokenizer:
    def __call__(self, doc):
        return [tok for tok in jieba.cut(doc) if tok.strip()]


class SplitTokenizer:
    def __call__(self, doc):
        return str.split(doc)


def get_auto_n_jobs(fraction=0.5, max_jobs=16):
    """
    智能分配 CPU 核心数，用于设置 sklearn 的 n_jobs 参数。

    参数:
    fraction: 使用总核数的比例（如 0.5 表示一半）
    max_jobs: 最大允许使用的核心数（防止过多）

    返回:
    合理的 n_jobs 整数值
    """
    total_cores = multiprocessing.cpu_count()
    suggested = int(total_cores * fraction)
    n_jobs = min(max(1, suggested), max_jobs)
    return n_jobs


class FitTextMatcher:
    """
    高性能文本匹配器
    基于 TF-IDF + 最近邻搜索实现相似文献查找
    """

    def __init__(self, algorithm='brute', metric='cosine', n_jobs=-1, tokenizer=JiebaTokenizer()):
        """
        初始化文本匹配器

        参数:
        algorithm: 搜索算法 ('brute', 'kd_tree', 'ball_tree', 'lshf')
        metric: 距离度量 ('cosine', 'euclidean', 'manhattan')
        n_jobs: 并行作业数 (-1 表示使用所有CPU核心)
        """
        self.vectorizer = TfidfVectorizer(
            max_features=None,  # 限制特征数量以提高性能
            tokenizer=tokenizer,
            stop_words=None,  # 中文不适用 'english'
            ngram_range=(1, 2)  # 使用单字和双字组合
        )

        self.nn = NearestNeighbors(
            algorithm=algorithm,
            metric=metric,
            n_jobs=n_jobs  # 并行处理加速搜索
        )

        self.corpus = None
        self.corpus_size = 0

    def fit(self, corpus):
        """
        训练匹配器
        """
        self.corpus = corpus
        self.corpus_size = len(corpus)
        print(f"处理 {self.corpus_size} 篇文献...")

        # 向量化文本
        start_time = time.time()
        X = self.vectorizer.fit_transform(corpus)
        vectorization_time = time.time() - start_time
        print(f"TF-IDF 向量化完成, 耗时: {vectorization_time:.4f}秒")
        print(f"特征维度: {X.shape[1]}")

        # 训练最近邻模型
        start_time = time.time()
        self.nn.fit(X)
        training_time = time.time() - start_time
        print(f"最近邻模型训练完成, 耗时: {training_time:.4f}秒")

        return self

    def save(self, path, name):
        """
        保存模型和向量器
        """
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.vectorizer, os.path.join(path, name + "_vectorizer.joblib"))
        joblib.dump(self.nn, os.path.join(path, name + "_nn_model.joblib"))
        joblib.dump(self.corpus, os.path.join(path, name + "_corpus.joblib"))
        print(f"模型保存至 {path}")
        return self

    def get_save_bytes_io(self, idx_list=None):
        """
        保存模型和向量器
        """
        if idx_list is None:
            idx_list = []

        result_list = []
        for i in [self.vectorizer, self.nn, self.corpus, idx_list]:
            temp_io = create_gzip_joblib(i)
            result_list.append(temp_io)
        print(f"获取模型字节码成功")
        return result_list

    def load(self, path, name):
        """
        从文件加载模型
        """
        self.vectorizer = joblib.load(os.path.join(path, name + "_vectorizer.joblib"))
        self.nn = joblib.load(os.path.join(path, name + "_nn_model.joblib"))
        self.corpus = joblib.load(os.path.join(path, name + "_corpus.joblib"))
        self.corpus_size = len(self.corpus)
        print(f"模型从 {path} 加载完成，共 {self.corpus_size} 篇文献")
        return self

    def load_bytes(self, vec, nn, corpus, idx):
        # 解压并加载对象
        with gzip.GzipFile(fileobj=vec, mode='rb') as gz:
            self.vectorizer = joblib.load(gz)
        with gzip.GzipFile(fileobj=nn, mode='rb') as gz:
            self.nn = joblib.load(gz)
        with gzip.GzipFile(fileobj=corpus, mode='rb') as gz:
            self.corpus = joblib.load(gz)
        with gzip.GzipFile(fileobj=idx, mode='rb') as gz:
            self.idx = joblib.load(gz)
        self.corpus_size = max(len(self.corpus), len(self.idx))
        print(f"加载bytes完成，共 {self.corpus_size} 篇文献")
        return self

    def search(self, query, n=5, return_scores=True):
        """
        查找相似文献

        参数:
        query: 查询文本
        n: 返回最相似文献的数量
        return_scores: 是否返回相似度分数

        返回:
        匹配的文献索引和相似度分数
        """
        if self.corpus is None:
            raise ValueError("请先使用 fit() 方法训练模型")

        # 向量化查询文本
        query_vec = self.vectorizer.transform([query])

        # 查找最近邻
        start_time = time.time()
        distances, indices = self.nn.kneighbors(query_vec, n_neighbors=n)
        search_time = time.time() - start_time

        # print(f"搜索完成, 耗时: {search_time:.6f}秒")

        # 将距离转换为相似度 (余弦距离 = 1 - 余弦相似度)
        similarities = 1 - distances

        # 返回结果
        if return_scores:
            return indices[0], similarities[0]
        return indices[0]

    def batch_search(self, queries, n=5, return_scores=True):
        """
        批量查找相似文献（一次处理多条 query）

        参数:
        queries: 查询文本列表
        n: 每条 query 返回多少条相似文献
        return_scores: 是否返回相似度分数

        返回:
        一个列表，包含每条 query 的匹配索引和相似度 [(indices1, sims1), (indices2, sims2), ...]
        """
        if self.corpus is None:
            raise ValueError("请先使用 fit() 方法训练模型")

        start_time = time.time()

        # 向量化所有 query，一次性
        query_vecs = self.vectorizer.transform(queries)

        # 查找最近邻
        distances, indices = self.nn.kneighbors(query_vecs, n_neighbors=n)
        search_time = time.time() - start_time
        # print(f"批量搜索完成，共 {len(queries)} 条，耗时: {search_time:.4f}秒")

        if return_scores:
            similarities = 1 - distances
            return indices, similarities
        return indices

    def explain_match(self, query, index):
        """
        解释匹配结果 - 显示查询和匹配文献的关键词
        """
        # 获取TF-IDF特征名
        feature_names = self.vectorizer.get_feature_names_out()

        # 向量化查询和匹配文献
        query_vec = self.vectorizer.transform([query])
        doc_vec = self.vectorizer.transform([self.corpus[index]])

        # 获取重要特征
        query_data = zip(feature_names, query_vec.toarray()[0])
        doc_data = zip(feature_names, doc_vec.toarray()[0])

        # 筛选非零特征
        query_keywords = [(word, score) for word, score in query_data if score > 0]
        doc_keywords = [(word, score) for word, score in doc_data if score > 0]

        # 按重要性排序
        query_keywords.sort(key=lambda x: x[1], reverse=True)
        doc_keywords.sort(key=lambda x: x[1], reverse=True)

        # 打印结果
        print(f"\n匹配文献 #{index} 解释:")
        print(f"查询关键词: {[word for word, _ in query_keywords[:10]]}")
        print(f"文献关键词: {[word for word, _ in doc_keywords[:10]]}")

        # 计算共同关键词
        common_keywords = set([word for word, _ in query_keywords[:20]]) & set([word for word, _ in doc_keywords[:20]])
        print(f"共同关键词: {list(common_keywords)}")

        return common_keywords