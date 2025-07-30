import copy
import re
import string

import regex
from jellyfish import damerau_levenshtein_distance
from rapidfuzz._utils import setupPandas, is_none
from rapidfuzz.distance import Jaro
from unidecode import unidecode

from re_common.v2.baselibrary.utils.stringutils import get_diacritic_variant

"""
作者比率分布 大部分在 1和 2 
1-2 675092763
2-3 49335191
3-4 440848
4-5 9953
其他都是几百 几十和几个 不用考虑
如果 大于5 大降分
3-4 4-5 分两个段降分 3-4 降得最少
1-3 不降分
"""

additional_chars = '‑–‐’·．—'
extended_punctuation = string.punctuation + additional_chars


def detect_other_languages(text):
    # 匹配所有非中文、非英文、非数字字符
    pattern = r'[^\u4E00-\u9FFFa-zA-Z0-9\s.,!?;:\'\"()‑\-–—‐’·˜．]'

    # 使用正则表达式查找
    matches = re.findall(pattern, text)

    # 如果找到匹配的字符，表示存在非中文、非英文、非数字的语言字符
    return bool(matches)


def extract_initials(text):
    # 按空格分隔字符串
    words = text.split()

    # 提取每个单词的首字母并转化为大写
    initials = ''.join(word[0].upper() for word in words)

    return initials


def is_contained(str1, str2):
    # 判断是否是包含关系
    return str1 in str2 or str2 in str1


# list1 是否包含 list2 如果包含 return True
def is_contained_list(list1, list2):
    # 检查 list2 中每个元素的出现次数，是否能在 list1 中找到足够的数量
    for item in list2:
        if list2.count(item) > list1.count(item):
            return False
    return True


def check_common_elements_by_length_rank(list1, list2):
    # 获取两个列表的交集
    set1 = set(list1)
    set2 = set(list2)

    common_elements = set1 & set2  # 获取交集

    if not common_elements:
        return False

    # 确定较短的列表
    short_list = list1 if len(list1) < len(list2) else list2

    # 按字符长度排序短列表
    sorted_short_list = sorted(short_list, key=len)

    for word in common_elements:
        # 获取该单词在短列表中的字符长度排名
        length_rank = sorted_short_list.index(word) + 1  # +1 因为列表索引从0开始
        # 如果单个字母跳过
        if len(word) == 1:
            continue

        if length_rank / len(sorted_short_list) > 0.5:
            # 说明 命中了长字符串相等
            return True

    return False


def remove_punctuation(text):
    # 20241226 替换掉自定义符号集
    text = regex.sub("[\\p{P}￥+=˛`$<¸´~^￥≤℃×■¨°>|ⅰⅱⅲⅳⅴⅵⅶⅹⅺⅻ]", "", text.lower())
    # text = text.translate(str.maketrans('', '', extended_punctuation))
    return text


def space_punctuation(text):
    # 使用空格替换符号
    return text.translate(str.maketrans(extended_punctuation, ' ' * len(extended_punctuation), ''))


def custom_rstrip(s):
    # 去除尾部的指定子串，顺序删除
    s = s.strip()
    if s.endswith("."):
        s = s[:-1]  # 删除最后的 "."
    s = s.strip()
    if s.endswith("jr"):
        s = s[:-2]  # 删除最后的 "jr"
    s = s.strip()
    if s.endswith(","):
        s = s[:-1]  # 删除最后的 ","
    s = s.strip()

    return s


# 分割中文拼音，如"Xiaohong" ————> ['Xiao', 'hong']
def chinese_pinyin_split_by_rules(input_str):
    # 声母列表（含复合声母）
    initials = {
        'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h',
        'j', 'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w'
    }
    # 韵母列表（部分示例）
    finals = {
        'a', 'o', 'e', 'ai', 'ei', 'ao', 'ou', 'an', 'en', 'ang', 'eng', 'ong',
        'i', 'ia', 'ie', 'iao', 'iu', 'ian', 'in', 'iang', 'ing', 'iong',
        'u', 'ua', 'uo', 'uai', 'ui', 'uan', 'un', 'uang', 'ueng',
        'v', 've', 'van', 'vn'
    }
    result = []
    while input_str:
        # 尝试匹配最长声母
        max_initial_len = 2  # 最长声母如 'zh'
        matched_initial = ""
        for length in range(max_initial_len, 0, -1):
            candidate = input_str[:length]
            if candidate.lower() in initials:
                matched_initial = candidate
                break
        # 切分声母后的剩余部分
        remaining = input_str[len(matched_initial):]
        # 匹配韵母
        max_final_len = min(4, len(remaining))  # 最长韵母如 'iong'
        matched_final = ""
        for length in range(max_final_len, 0, -1):
            candidate = remaining[:length]
            if candidate.lower() in finals:
                matched_final = candidate
                break
        if matched_final:
            # 合并声母和韵母
            syllable = matched_initial + matched_final
            result.append(syllable)
            input_str = input_str[len(syllable):]
        else:
            return []  # 无法切分
    return result


def AuthorRatio(
        s1,
        s2,
        *,
        processor=None,
        score_cutoff=None,
        is_delete_jr=True,
):
    # 判空需要
    setupPandas()
    # 如果为空就没有相似度
    if is_none(s1) or is_none(s2):
        return 0

    # 处理字符串的程序 外围传入方法
    if processor is not None:
        s1 = processor(s1)
        s2 = processor(s2)

        # 处理后是否为空字符串，如果有 返回0
        if not s1 or not s2:
            return 0
    # get_diacritic_variant(unidecode(strs)) 更激进，会丢失非拉丁字符和原文信息，适合需要把多语言文本转换成 ASCII 拼音的场景。
    # 处理音标问题
    s1 = get_diacritic_variant(unidecode(s1))
    s2 = get_diacritic_variant(unidecode(s2))
    # 这里提出来是为了少计算 但后期需要平衡内存和算力
    # 移除指定符号 这里做了小写化处理
    s1_punc = remove_punctuation(s1)
    s2_punc = remove_punctuation(s2)
    # 分成列表
    s1_punc_split = s1_punc.split()
    s2_punc_split = s2_punc.split()

    def compare_strings(s1_punc, s2_punc):
        # 去除字符串中的空白字符
        cleaned_s1 = re.sub(r'\s+', '', s1_punc)
        cleaned_s2 = re.sub(r'\s+', '', s2_punc)

        # 如果两个字符串相等，返回 相等
        if cleaned_s1 == cleaned_s2:
            return "equal"
        # 如果一个字符串包含另一个字符串，返回 子字符串
        elif cleaned_s1 in cleaned_s2 or cleaned_s2 in cleaned_s1:
            return "subset"
        # 否则返回 无关
        else:
            return "unrelated"

    # 如果去除符号后相等 那么就是100% 的相同作者 这里主要防止顺序颠倒的问题
    if len(s1_punc_split) == len(s2_punc_split) and set(s1_punc_split) == set(s2_punc_split):
        return 1

    # 如果少一个单词，认为是正确的包含关系，在简写中会出现这种情况
    if is_contained_list(s1_punc_split, s2_punc_split) or is_contained_list(s2_punc_split, s1_punc_split):
        return 0.98

    rus = compare_strings(s1_punc, s2_punc)
    # 如果顺序去字符 去空格完全相等 那么作者相同 “Hoorani, H. R.” -> 'Hoorani, HR'
    if rus == "equal":
        return 1

    # 在外文中 jr 代表儿子 我现在需要去掉这个字符带来的影响,可以用参数控制
    if is_delete_jr:
        s1_n = custom_rstrip(s1.lower())
        s1 = s1[:len(s1_n)]
        s2_n = custom_rstrip(s2.lower())
        s2 = s2[:len(s2_n)]

    # 这里正向是为了解决 Liao, Zhan -> Liao Z. 这样的关系 但是反向会导致上面的错误存在
    if len(s1_punc_split) == len(s2_punc_split) and rus == "subset":
        if len(s1_punc_split[-1]) == 1 or len(s2_punc_split[-1]) == 1:
            if s1_punc_split[0] == s2_punc_split[0] and s1_punc_split[-1][:1] == s2_punc_split[-1][:1]:
                return 1
        # return 0.96   # 如果单词数一致 是包含关系 但会出现这样的 Li Li 和 Li Liang 会被判定为一样 所以这里不给满分

    # 使用正则表达式替换多个空格为一个空格
    l1 = re.sub(r'\s+', ' ', space_punctuation(s1.replace("'", "")).strip()).strip().split()
    l2 = re.sub(r'\s+', ' ', space_punctuation(s2.replace("'", "")).strip()).strip().split()

    def is_same_or_initials_match(l1, l2):
        """
        判断两个字符串是否完全相同，或者它们的首字母是否相同。
        bool: 如果两个字符串完全相同，或它们的首字母匹配，返回 True；否则返回 False。
        """

        # 使用 zip() 同时遍历 l1 和 l2 中的字符
        for i1, i2 in zip(l1, l2):
            # 如果两个字符忽略大小写后相同，继续比较下一个字符
            if i1.lower() == i2.lower():
                continue
            # 在作者中 有可能错误字母 当单词大于3 且只有一个字母错误或者位置交换时 可以认为这两个单词相同
            # 样例 "De Gusmio, Ana Paula Henriques","De Gusmão, Ana Paula Henriques"
            if len(i1) > 3 and damerau_levenshtein_distance(i1, i2) <= 1:
                continue

            # 如果其中一个字符的长度为1（即是单个字母），检查它们的首字母是否匹配
            if len(i1) == 1 or len(i2) == 1:
                # 比较它们的首字母（不区分大小写）
                if i1[0].upper() == i2[0].upper():
                    continue
                else:
                    return False  # 如果首字母不同，则返回 False

            # 如果上面条件都不满足，说明字符不匹配，直接返回 False
            return False

        # 如果循环结束都没有提前返回 False，则表示两个字符串完全匹配，返回 True
        return True

    # 防止清理后 一方变为空字符串
    if len(l1) == 0 or len(l2) == 0:
        return 0

    #  这里的逻辑是最后的位置全大写就将他拆分散 比如 joi CJ -> joi C J
    if len(l1[-1]) != 1 and l1[-1].isupper():
        t_str = l1[-1]
        l1 = l1[:-1]
        l1.extend(list(t_str))
    if len(l2[-1]) != 1 and l2[-1].isupper():
        t_str = l2[-1]
        l2 = l2[:-1]
        l2.extend(list(t_str))

    # 如果长度相等 简写也是单词的首字母 那么两个名字一致 举例:"María M.Martorell", "Martorell, María M."
    if len(l1) == len(l2) and (is_same_or_initials_match(l1, l2) or set(l1) == set(l2)):
        return 1

    # 在这里针对上面一条算法再增加一条算法，先对list 排序在对他进行上面的对比
    # 如果长度相等 简写也是单词的首字母 那么两个名字一致 举例:Guo, Qiang @@ Q. Guo
    sort_l1 = copy.deepcopy(l1)
    sort_l2 = copy.deepcopy(l2)
    sort_l1.sort()
    sort_l2.sort()
    if len(sort_l1) == len(sort_l2) and (is_same_or_initials_match(sort_l1, sort_l2) or set(sort_l1) == set(sort_l2)):
        return 0.99


    ##############################################################
    # 以上为情况穷举情况，以下为其他情况的相似率计算
    ##############################################################

    # 设置score_cutoff 默认值为0
    if score_cutoff is None:
        score_cutoff = 0

    len1 = len(s1)
    len2 = len(s2)
    # 用长字符串除以 短字符串 得到字符串长度的比率
    len_ratio = len1 / len2 if len1 > len2 else len2 / len1

    # 计算归一化的 Indel 相似度。 对于比率<score_cutoff，返回0。
    end_ratio = normal_end_ratio = Jaro.normalized_similarity(s1.lower(), s2.lower())

    # 需要对作者的比率分布进行调研决定哪些是小比率哪些是大比率
    if len_ratio > 1.5 and len_ratio < 3:
        # 计算线性下降的减分比例
        # 当 len_ratio = 1.5 时，reduction_factor = 1.0
        # 当 len_ratio = 3.0 时，reduction_factor = 0.9
        reduction_factor = 1.0 - (len_ratio - 1.5) * (0.1 / 1.5)
        end_ratio = end_ratio * reduction_factor
    if len_ratio > 3 and len_ratio < 4:  # 应该少量降分
        end_ratio = end_ratio * 0.9
    if len_ratio > 4 and len_ratio < 5:  # 应该中量降分
        end_ratio = end_ratio * 0.8
    if len_ratio > 5:  # 应该降分
        end_ratio = end_ratio * 0.7

    # 变音提分已经在上面解决了
    # # 非英语 非汉语提分 与 英文对比时 提分
    # if any([detect_other_languages(s1), detect_other_languages(s2)]) and not all([detect_other_languages(s1),
    #                                                                               detect_other_languages(s2)]):
    #     # 应该提分
    #     end_ratio = end_ratio * 1.1

    # 首字母相同提分
    # if is_contained(extract_initials(s1), extract_initials(s2)):
    if is_contained_list([i[:1].lower() for i in l1], [i[:1].lower() for i in l2]):
        # 应该提分
        end_ratio = end_ratio * 1.05
    else:
        end_ratio = end_ratio * 0.9

    if len(l1) != len(l2):
        end_ratio = end_ratio * 0.92

    # 相同部分在短的数据的词中的长度位置 如果是简写相同 不应该提分
    if check_common_elements_by_length_rank(l1, l2) and len_ratio > 1.5:
        # 应该提分
        end_ratio = end_ratio * 1.1

    if l1[0] != l2[0]:
        end_ratio = end_ratio * Jaro.normalized_similarity(l1[0].lower(), l2[0].lower())

    # 如果字符串本身的相似度高 应该拉上去 否者应该拉下来
    return min(end_ratio, 1) * 0.5 + normal_end_ratio * 0.5
