import Levenshtein
import jellyfish
from rapidfuzz.distance import DamerauLevenshtein, Hamming, Indel, LCSseq, OSA


class BaseStringSimilarity(object):

    @classmethod
    def levenshtein_similarity(cls, str1, str2) -> float:
        """
        返回 两个字字符串之间的编辑距离 分数
        """
        # 编辑距离长度
        distance = Levenshtein.distance(str1, str2)
        # 以最长字符串为除数算分
        similarity = 1 - (distance / max(len(str1), len(str2)))
        return similarity

    @classmethod
    def damerau_normalized_distance_similarity(cls, str1, str2) -> float:
        """
          # 计算 归一化的编辑距离，取值范围 [0, 1]，值越小表示越相似。 一般不以小评估分 所以不用
        similarity = DamerauLevenshtein.normalized_distance(str1, str2)
        作用：计算 相似度得分，取值范围 [0, max_len]，值越大表示越相似。
        print(DamerauLevenshtein.similarity(str1, str2))
        """
        # 该算法与 cls.levenshtein_similarity 算法一致 只是 编辑距离的得值不一样
        similarity = DamerauLevenshtein.normalized_similarity(str1, str2)
        return similarity

    @classmethod
    def indel_levenshtein_similarity(cls, str1, str2) -> float:
        """
        本质上使用的 是 Indel.normalized_similarity(str1,str2) 方法

        计算 str1 和 str2 之间的 Indel 距离（插入和删除操作的最小次数）
        Indel.distance(str1, str2)
        计算 标准化后的 Indel 距离，取值范围在 [0, 1] 之间，其中 0 表示完全相同，1 表示完全不同。 ``distance / (len1 + len2)``.
        Indel.normalized_distance(str1, str2)
        计算 [max, 0] 范围内的 Indel 相似度。计算公式为“(len1 + len2) - distance”
        Indel.similarity(str1, str2)
        计算 [0, 1] 范围内的归一化插入/缺失相似度。计算公式为“1 - normalized_distance”
        Indel.normalized_similarity(str1, str2)

        """
        # 计算相似度（0到1之间的值，1表示完全相同）
        similarity = Levenshtein.ratio(str1, str2)
        return similarity

    @classmethod
    def jaro_similarity(cls, str1, str2) -> float:
        """
        Jaro 相似度是一种用于测量两个字符串相似度的算法，主要考虑：
        匹配的字符
        字符顺序
        字符转置（位置交换）

        与 Jaro.normalized_similarity(str1,str2) 一致
        """
        return jellyfish.jaro_similarity(str1, str2)

    @classmethod
    def jaro_winkler_similarity(cls, str1, str2) -> float:
        """
        Jaro-Winkler 是 Jaro 的改进版，对前缀匹配给予更多权重

        与 JaroWinkler.normalized_similarity(str1,str2) 结果一致

        print(JaroWinkler.distance(str1, str2))
        与 print(JaroWinkler.normalized_distance(str1, str2)) 结果一致

        print(JaroWinkler.similarity(str1, str2))
        与 print(JaroWinkler.normalized_similarity(str1,str2)) 结果一致
        """
        return jellyfish.jaro_winkler_similarity(str1, str2)

    @classmethod
    def osa_similarity(cls, str1, str2) -> float:
        """
        计算 [0, 1] 范围内的归一化最佳字符串比对 (OSA) 相似度。

        计算公式为“1 - normalized_distance”
        """
        return OSA.normalized_similarity(str1, str2)

    @classmethod
    def lcs_seq_similarity(cls, str1, str2) -> float:
        """
        计算 [0, 1] 范围内的归一化 LCS 相似度。
        计算公式为“1 - normalized_distance”
        """
        return LCSseq.normalized_similarity(str1, str2)

    @classmethod
    def lcs_seq_distance(cls, str1, str2) -> int:
        """
        LCSseq.distance 是 RapidFuzz 库中的一个方法，用于计算两个字符串之间的 最长公共子序列（Longest Common Subsequence, LCS）距离。
        LCS 是指两个字符串中 按顺序出现但不一定连续 的最长子序列。例如：
        "abcde" 和 "ace" 的 LCS 是 "ace"（长度 3）。
        "Druitt, Robert" 和 "Druitt R." 的 LCS 可能是 "Druitt R"（长度 8）。
        计算 [0, max] 范围内的 LCS 距离。
        计算公式为“max(len1, len2) - 相似度”。
        """
        return LCSseq.distance(str1, str2)

    @classmethod
    def osa_distance(cls, str1, str2) -> int:
        """
        OSA.distance（Optimal String Alignment，最优字符串对齐距离）是 RapidFuzz 库中的一个方法，用于计算两个字符串之间的 编辑距离（Edit Distance），但比标准的 Levenshtein 距离 限制更严格。

        OSA 额外允许 相邻字符交换（Transposition），但限制比 Damerau-Levenshtein 更严格（Damerau 允许多次交换，而 OSA 仅限一次）。
        """
        return OSA.distance(str1, str2)

    @classmethod
    def levenshtein_distance(cls, str1, str2) -> int:
        """
        返回 两个字字符串之间的编辑距离 分数
        标准 Levenshtein 距离 允许 插入、删除、替换 三种操作，但不允许 相邻字符交换（transposition）

        jellyfish.levenshtein_distance(str1,str2) 该方法结果与 本方法一致

        print(Jaro.distance(str1, str2))
        与 print(Jaro.normalized_distance(str1, str2)) 结果一致

        print(Jaro.similarity(str1, str2))
        与 print(Jaro.normalized_similarity(str1,str2)) 结果一致
        """
        # 编辑距离长度
        distance = Levenshtein.distance(str1, str2)
        print(jellyfish.levenshtein_distance(str1, str2))
        return distance

    @classmethod
    def indel_distance(cls, str1, str2) -> int:
        """
        Indel（Insertion + Deletion）距离是 仅考虑插入和删除操作 的编辑距离，不考虑替换操作。
        """
        return Indel.distance(str1, str2)

    @classmethod
    def damerau_levenshtein_distance(cls, str1, str2) -> int:
        """
        Damerau-Levenshtein 距离是 Levenshtein 距离的修改，它将换位（例如将 ifsh 表示为 fish）计为一次编辑
        """
        # 编辑距离长度
        distance = jellyfish.damerau_levenshtein_distance(str1, str2)
        print(DamerauLevenshtein.distance(str1, str2))
        return distance

    @classmethod
    def hamming_distance(cls, str1, str2) -> int:
        return Hamming.distance(str1, str2)

# str1 = "primulina elegant ladyis a new culitvar developed by crossing seed parent primulina medica and pollen parent primulina longii it has fresh and elegant flowershigh ornamental value and strong shade tolerance it is easy to cultivate and propagate"
# str2 = "primulinaelegant labyis a new cultivar developed by crossing seed parent primulina medica and pollen parent primulina longii it has fresh and elegant flowershigh ornamental value and strong shade tolerance it is easy to cultivate and propagate 2019 editorial office of acta horticulturae sinica all rights reserved"
# # str1 = "primulina elegant ladyis a new cultivar developed by crossing seed parent primulina medica and pollen parent primulina longii it has fresh and elegant flowershigh ornamental value and strong shade tolerance it is easy to cultivate and propagate"
# # str2 = "primulinaelegant ladyis a new cultivar developed by crossing seed parent primulina medica and pollen parent primulina longii it has fresh and elegant flowershigh ornamental value and strong shade tolerance it is easy to cultivate and propagate 2019 editorial office of acta horticulturae sinica all rights reserved"
