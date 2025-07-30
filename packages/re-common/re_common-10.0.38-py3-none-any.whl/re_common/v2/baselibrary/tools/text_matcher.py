import pickle

import jieba
import re
from typing import List, Dict, Tuple, Set, Optional, Union, Hashable, Protocol
from datasketch import MinHash, MinHashLSH

from re_common.v2.baselibrary.decorators.utils import deprecated
from re_common.v2.baselibrary.utils.string_bool import is_single_cjk_char


@deprecated("请使用 TextMatcherV2 代替。")
class TextMatcher(object):
    def __init__(
            self,
            threshold: float = 0.5,
            num_perm: int = 128,
            is_raw_texts=True,
            stopwords_path: Optional[str] = None,
            user_dict_path: Optional[str] = None,

    ):
        """
        初始化文本匹配器

        Args:
            threshold: LSH 相似度阈值
            num_perm: MinHash 排列数
            stopwords_path: 停用词文件路径
            user_dict_path: 用户自定义词典路径
        """
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        # self.minhashes: Dict[str, MinHash] = {}
        self.raw_texts: Dict[str, str] = {}
        self.is_raw_texts = is_raw_texts
        self.doc_counter = 0

        # 加载停用词
        self.stopwords: Set[str] = set()
        if stopwords_path:
            self.load_stopwords(stopwords_path)

        # 加载用户词典
        if user_dict_path:
            jieba.load_userdict(user_dict_path)

    def load_stopwords(self, stopwords_path: str) -> None:
        """加载停用词"""
        with open(stopwords_path, "r", encoding="utf-8") as f:
            self.stopwords = set(line.strip() for line in f)

    def preprocess_text(self, text: str) -> str:
        """
        文本预处理
        """
        # 转换为小写
        text = text.lower()
        # 移除特殊字符
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)
        # 移除多余空格
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        分词并移除停用词
        """
        words = jieba.lcut(text)
        one_char_size = len([i for i in words if len(i) == 1])
        all_size = len(words)
        if all_size != 0 and one_char_size / all_size > 0.6:
            words = [i for i in text.split() if i.strip()]

        # 过滤停用词和空字符
        words = [w for w in words if w not in self.stopwords and w.strip()]
        return words

    def create_minhash(self, words: List[str]) -> MinHash:
        """
        为分词结果创建 MinHash
        """
        minhash = MinHash(num_perm=self.num_perm)
        for word in words:
            minhash.update(word.encode("utf-8"))
        return minhash

    def add_document(self, text: str, doc_id: Optional[str] = None) -> str:
        """
        添加文档到索引

        Args:
            text: 文档文本
            doc_id: 文档ID（可选）

        Returns:
            doc_id: 文档ID
        """
        if doc_id is None:
            doc_id = f"doc_{self.doc_counter}"
            self.doc_counter += 1

        # 预处理和分词
        processed_text = self.preprocess_text(text)
        words = self.tokenize(processed_text)

        # 创建 MinHash
        minhash = self.create_minhash(words)
        if self.is_raw_texts:
            # 存储原始文本和 MinHash
            self.raw_texts[doc_id] = text
        # self.minhashes[doc_id] = minhash

        # 添加到 LSH
        self.lsh.insert(doc_id, minhash)

        return doc_id

    def batch_add_documents(self, texts: Dict[str, str]) -> None:
        """
        批量添加文档

        Args:
            texts: {doc_id: text} 的字典
        """
        for doc_id, text in texts.items():
            self.add_document(text, doc_id)

    def create_query_minhash(self, query: str):

        # 预处理查询文本
        processed_query = self.preprocess_text(query)
        query_words = self.tokenize(processed_query)
        # print(query_words)
        query_minhash = self.create_minhash(query_words)
        return query_minhash

    def find_similar(self, query_minhash: MinHash, return_similarities: bool = False) -> Union[
        List[str], List[Tuple[str, float]]]:
        """
        查找相似文档

        Args:
            query: 查询文本
            return_similarities: 是否返回相似度分数

        Returns:
            如果 return_similarities 为 True，返回 [(doc_id, similarity), ...]
            否则返回 [doc_id, ...]
        """

        # 使用 LSH 查找候选集
        similar_docs = self.lsh.query(query_minhash)

        # if return_similarities:
        #     # 计算精确的 Jaccard 相似度
        #     results = []
        #     for doc_id in similar_docs:
        #         similarity = query_minhash.jaccard(self.minhashes[doc_id])
        #         results.append((doc_id, similarity))
        #     # 按相似度降序排序
        #     return sorted(results, key=lambda x: x[1], reverse=True)

        return similar_docs

    def get_text(self, doc_id: str) -> Optional[str]:
        """获取原始文本"""
        if self.is_raw_texts:
            return self.raw_texts.get(doc_id)
        raise Exception("没有开启存储")

    def remove_document(self, doc_id: str) -> bool:
        """
        删除文档

        Returns:
            bool: 是否成功删除
        """
        # if doc_id not in self.minhashes:
        #     return False

        self.lsh.remove(doc_id)
        # del self.minhashes[doc_id]
        if self.is_raw_texts:
            del self.raw_texts[doc_id]
        return True

    def clear(self) -> None:
        """清空所有数据"""
        self.lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        # self.minhashes.clear()
        self.raw_texts.clear()
        self.doc_counter = 0


# 定义一个协议，描述“像鸭子一样”的行为
class TokenizeDuckLike(Protocol):
    def get_words(self, text) -> List:
        pass


class JiebaTokenize(object):

    def __init__(self, stopwords=None):
        self.stopwords = stopwords

    def get_words(self, text) -> List:

        if self.stopwords is None:
            stopwords = []
        words = jieba.lcut(text)

        # 统计单字符数据 长度，防止结巴分词分不了的单词 将数据分为单个字符

        # 这里为什么使用函数 而不是在推导式中兼容，主要是在一些 spark中 推导式的if 条件不遵循最短路径原则会将表达式当做一个整体算子
        def is_singel_en(i):
            if len(i) == 1 and not is_single_cjk_char(i):
                return True
            return False

        one_char_size = len([i for i in words if is_singel_en(i)])
        all_size = len(words)
        # 如果单字符个数超过一定比例 就直接用空格分词
        if all_size != 0 and one_char_size / all_size > 0.6:
            words = [i for i in text.split() if i.strip()]

        # 过滤停用词和空字符
        words = [w for w in words if w not in stopwords and w.strip()]
        return words


class TextMatcherV2(object):

    def __init__(
            self,
            threshold: float = 0.5,
            num_perm: int = 128,
            tdk: TokenizeDuckLike = None
    ):
        """
        初始化文本匹配器

        Args:
            threshold: LSH 相似度阈值
            num_perm: MinHash 排列数
            stopwords_path: 停用词文件路径
            user_dict_path: 用户自定义词典路径
        """
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        self.tdk = tdk

    def add_document(self, doc_id: str, minhash: Union[MinHash, str], tdk: TokenizeDuckLike = None):
        if isinstance(minhash, str):
            minhash = self.str_to_minihash(minhash, tdk)

        self.lsh.insert(doc_id, minhash)

    def batch_add_documents(self, betch_data: Union[list, dict], tdk: TokenizeDuckLike = None):
        def _add_document(minhash_or_str, tdk):
            if isinstance(minhash_or_str, str):
                minhash_or_str = self.str_to_minihash(minhash_or_str, tdk)
            self.add_document(docid, minhash_or_str, tdk)

        if isinstance(betch_data, list):
            # 必须是可解包的2个数据的元组或list
            for docid, minhash_or_str in betch_data:
                _add_document(minhash_or_str, tdk)
        elif isinstance(betch_data, dict):
            for docid, minhash_or_str in betch_data.items():
                _add_document(minhash_or_str, tdk)
        else:
            raise Exception("数据类型错误")

    def find_similar(self, query_minhash: Union[MinHash, str], tdk: TokenizeDuckLike = None) -> List[Hashable]:
        # 使用 LSH 查找候选集
        if isinstance(query_minhash, str):
            query_minhash = self.str_to_minihash(query_minhash, tdk)
        similar_docs = self.lsh.query(query_minhash)
        return similar_docs

    def create_minhash(self, words: List[str], num_perm=None) -> MinHash:
        """
        为分词结果创建 MinHash
        """
        if num_perm is None:
            num_perm = self.num_perm
        minhash = MinHash(num_perm=num_perm)
        for word in words:
            minhash.update(word.encode("utf-8"))
        return minhash

    def create_words(self, text: str, tdk: TokenizeDuckLike = None):
        if tdk is None:
            tdk = self.tdk
        worlds = tdk.get_words(text)
        return worlds

    def str_to_minihash(self, text: str, tdk: TokenizeDuckLike = None):
        if tdk is None:
            tdk = self.tdk
        words = self.create_words(text, tdk)
        minhash = self.create_minhash(words, self.num_perm)
        return minhash

    def minhash_dumps(self, minhash) -> bytes:
        """
        序列化
        """
        serialized_minhash = pickle.dumps(minhash)
        return serialized_minhash

    def minhash_loads(self, serialized_minhash) -> MinHash:
        """
        反序列化
        """
        minhash = pickle.loads(serialized_minhash)
        return minhash

    def merge_other_minhashlsh(self, other_minhashlsh: MinHashLSH):
        """
        在其他地方创建好的lsh 合并进来
        """
        self.lsh.merge(other_minhashlsh)
