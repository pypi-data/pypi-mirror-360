import logging
from itertools import groupby

logger = logging.getLogger(__name__)  # 创建 logger 实例


class BaseDict(object):
    @classmethod
    def flip_dict(cls, original_dict, raise_on_conflict=True):
        """
        翻转字典：将 key 是字符串、value 是列表的字典，转换为 key 是原 value 列表中的元素、value 是原 key 的字典。
        :param original_dict: 原始字典
        :param raise_on_conflict: 是否在键冲突时抛出异常，默认为 False
        :return: 翻转后的字典
        """
        flipped_dict = {}
        for key, value_list in original_dict.items():
            for value in value_list:
                if value in flipped_dict:
                    if raise_on_conflict:
                        raise ValueError(f"Key conflict detected: {value} already exists in the flipped dictionary.")
                    else:
                        # 覆盖冲突的键
                        logger.warning(
                            f"Warning: Key conflict detected for {value}. Overwriting with new value: {key}.")
                flipped_dict[value] = key
        return flipped_dict

    @classmethod
    def get_temp_gid_dicts(cls,lists,key_name):
        """
        对 列表字典 分组 组成 分组id的字典
        """
        dicts = {}
        for group_id, group_tmp in groupby(sorted(lists, key=lambda x: x[key_name]),
                                           key=lambda x: x[key_name]):
            dicts[group_id] = group_tmp
        return dicts