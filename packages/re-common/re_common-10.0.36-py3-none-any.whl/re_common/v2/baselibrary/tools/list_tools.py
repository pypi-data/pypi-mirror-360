import itertools
from typing import List, Any, Tuple


def check_no_duplicates_2d(lst_2d):
    """
        检查二维列表的每一行是否无重复
        如果有重复值 返回 False
        如果没有重复 返回True
    """
    for row in lst_2d:
        # 将行转为集合，比较长度
        if len(row) != len(set(row)):
            return False
    return True


def generate_cross_list_combinations(lists: List[List[Any]]) -> List[Tuple[Any, Any]]:
    """
    生成不同列表间的所有两两组合（元组长度为2）

    参数:
        lists: 包含多个列表的列表，例如 [[1,2], ['a','b'], ['x','y']]

    返回:
        包含所有跨列表两两组合的列表，每个组合是一个元组
        例如 [(1,'a'), (1,'b'), (2,'a'), ..., ('a','x'), ('a','y'), ...]
    """
    combinations = []
    for i in range(len(lists)):
        for j in range(i + 1, len(lists)):
            combinations.extend(itertools.product(lists[i], lists[j]))
    return combinations


def filter_and_sort_by_smi(all_list, top_n=1000):

    """
    要求 list 里面第一个是比较大小的数据 第二个是实际数据
    """

    # 1. 去重：按 doc_id 去重，保留 smi 最大的记录
    unique_dict = {}
    for smi, doc_id in all_list:
        if doc_id not in unique_dict or smi > unique_dict[doc_id][0]:
            unique_dict[doc_id] = (smi, doc_id)

    # 2. 转换为列表并排序
    unique_list = sorted(unique_dict.values(), key=lambda x: x[0], reverse=True)

    # 3. 取前 top_n 个
    return unique_list[:top_n]


def list_to_dict(list_data,key_name):
    # 使用 defaultdict 来处理重复 id
    from collections import defaultdict

    dict_data = defaultdict(list)

    for item in list_data:
        dict_data[item[key_name]].append(item)

    # 将 defaultdict 转换成普通字典
    dict_data = dict(dict_data)
    return dict_data

def split_list_by_step(lst, step=100):
    # 一维列表按照步长转换成二维列表
    return [lst[i:i + step] for i in range(0, len(lst), step)]