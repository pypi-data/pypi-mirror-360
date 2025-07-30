from typing import List

import jieba
from datasketch import MinHash, minhash

from re_common.v2.baselibrary.decorators.utils import deprecated
from re_common.v2.baselibrary.utils.string_bool import is_single_cjk_char

@deprecated("请使用 TextMatcherV2 中的方法代替。")
def tokenize(text: str, stopwords=None) -> List[str]:
    """
    分词并移除停用词
    """
    if stopwords is None:
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

@deprecated("请使用 TextMatcherV2 中的方法代替。")
def create_minhash(words: List[str], num_perm=128) -> MinHash:
    """
    为分词结果创建 MinHash
    """
    minhash = MinHash(num_perm=num_perm)
    for word in words:
        minhash.update(word.encode("utf-8"))
    return minhash

@deprecated("请使用 TextMatcherV2 中的方法代替。")
def get_str_minhash(title):
    from re_common.v2.baselibrary.utils.string_clear import rel_clear
    rel_title = rel_clear(title)
    if not rel_title:
        return ""
    words = tokenize(rel_title)
    minhash = create_minhash(words)
    return minhash
