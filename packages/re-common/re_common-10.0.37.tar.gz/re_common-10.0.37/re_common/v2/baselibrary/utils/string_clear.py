import re
from functools import lru_cache
from urllib.parse import unquote

import regex

from re_common.v2.baselibrary.utils.stringutils import (
    qj2bj,
    bj2qj,
    get_diacritic_variant,
    clean_html,
    remove_spaces_between_chinese_characters, clean_unicode_alnum, normalize_nfkc,
)


@lru_cache(maxsize=1)
def get_cc():
    from opencc import OpenCC

    # pip install opencc-python-reimplemented
    cc = OpenCC("t2s")  # t2s是繁体转简体
    return cc


class StringClear(object):
    def __init__(self, obj_str):
        self.obj_str = obj_str

    def None_to_str(self):
        if self.obj_str is None:
            self.obj_str = ""
        return self

    def to_str(self):
        self.obj_str = str(self.obj_str)
        return self

    def qj_to_bj(self):
        # 全角变半角
        self.obj_str = qj2bj(self.obj_str)
        return self

    def bj_to_qj(self):
        # 半角变全角
        self.obj_str = bj2qj(self.obj_str)
        return self

    def convert_to_simplified(self):
        # 繁体转简体
        self.obj_str = get_cc().convert(self.obj_str)
        return self

    def lower(self):
        self.obj_str = self.obj_str.lower()
        return self

    def upper(self):
        self.obj_str = self.obj_str.upper()
        return self

    def collapse_spaces(self):
        # 移除多余空格,连续多个空格变一个
        self.obj_str = re.sub(r"\s+", " ", self.obj_str)
        return self

    def clear_all_spaces(self):
        # 去除所有空格
        self.obj_str = re.sub("\\s+", "", self.obj_str)
        return self

    def clean_symbols(self):
        """
        清理已知的符号
        旧版: "[\\p{P}～`=￥×\\\\*#$^|+%&~!,:.;'/{}()\\[\\]?<> 《》”“\\-（）。≤《〈〉》—、·―–‐‘’“”″…¨〔〕°■『』℃ⅠⅡⅢⅣⅤⅥⅦⅩⅪⅫ]"
        """
        pattern = (
            r"[\p{P}"  # 所有 Unicode 标点符号
            r"～`=￥×\\*#$^|+%&~<> "  # 未被 \p{P} 覆盖的特殊符号
            r"”“\-≤—―–‐‘’“”″…¨°■℃"  # 其他未覆盖的标点和符号
            r"ⅠⅡⅢⅣⅤⅥⅦⅩⅪⅫ"  # 罗马数字
            r"]"
        )

        self.obj_str = regex.sub(
            pattern, "", self.obj_str
        )  # \\p{P} 标点符号 后面的是一些其他符号， 也可以用 \p{S} 代替 但是这个很广 可能有误伤
        return self

    def remove_special_chars(self):
        # 移除特殊字符，仅保留字母、数字、空格和汉字 \w 已经包括所有 Unicode 字母 下划线 _ 会被保留
        self.obj_str = re.sub(r"[^\w\s]", "", self.obj_str)
        return self

    def remove_all_symbols(self):
        # 一种更加强力的符号清理 只保留各个国家的字符 和各个国家的数字
        self.obj_str = clean_unicode_alnum(self.obj_str)
        return self

    def remove_underline(self):
        # 下划线在 \w 中 所以这里独立封装
        self.obj_str = re.sub("[_]", "", self.obj_str)
        return self

    def replace_dash_with_space(self):
        # 横杆转空格
        self.obj_str = self.obj_str.replace("-", " ")
        return self

    def strip_quotes(self):
        # 清理 双引号
        self.obj_str = self.obj_str.replace('"', "")
        return self

    def remove_diacritics(self):
        """
        和 clear_nkfc的关键区别 不去除连字
        """
        # 去除音标 转换成字母
        self.obj_str = get_diacritic_variant(self.obj_str)
        return self

    def clear_nkfc(self):
        self.obj_str = normalize_nfkc(self.obj_str)
        return self


    def remove_brackets(self):
        # 移除 方括号里面的内容
        self.obj_str = re.sub("\\[.*?]", "", self.obj_str)
        return self

    def remove_parentheses(self):
        # 移除圆括号的内容
        self.obj_str = re.sub("\\(.*?\\)", "", self.obj_str)
        return self

    def remove_html_tag(self):
        # 去除 html 标签
        import html

        self.obj_str = html.unescape(self.obj_str)

        self.obj_str = clean_html(self.obj_str)

        return self

    def remove_spaces_in_chinese_characters(self):
        # 匹配中文间的空格并替换为空字符串
        self.obj_str = remove_spaces_between_chinese_characters(self.obj_str)
        return self

    def url_to_str(self):
        """
        url 编码转字符
        """
        self.obj_str = unquote(self.obj_str)
        return self

    def ascii_text(self):
        # 只保留 ASCII 范围内的可见字符：空格(32) 到 ~ (126)
        self.obj_str = ''.join(c for c in self.obj_str if 32 <= ord(c) <= 126)
        return self


    def get_str(self):
        return self.obj_str


def rel_clear(str_obj):
    # 为融合数据定制的 清理规则
    return (
        StringClear(str_obj)
        .None_to_str()  # 空对象转str 防止空对象
        .to_str()  # 防止其他类型传入 比如 int double
        .qj_to_bj()  # 全角转半角
        .remove_html_tag()  # html标签清理
        .remove_special_chars()  # 移除特殊字符，仅保留字母、数字、空格和汉字 \w 已经包括所有 Unicode 字母 下划线 _ 会被保留
        .collapse_spaces()  # 移除多余空格,连续多个空格变一个
        .remove_spaces_in_chinese_characters()  # 匹配中文间的空格并替换为空字符串
        .convert_to_simplified()  # 繁体转简体
        .lower()  # 小写
        .get_str()  # 获取str
        .strip()
    )  # 去掉空格


def clear_au_organ(str_obj):
    """
    为作者机构定制的清理 与上面比除了不转小写外 还多了些特殊的清理
    """
    strs = (
        StringClear(str_obj)
        .None_to_str()  # None 转 空字符串
        .to_str()  # 防止其他类型传入 比如 int double
        .qj_to_bj()  # 全角转半角
        .strip_quotes()  # 清理 双引号
        .clean_symbols()  # 清理已知的符号
        .collapse_spaces()  # 移除多余空格,连续多个空格变一个
        .convert_to_simplified()  # 繁体转简体
        .get_str()  # 获取str
        .strip()  # 去掉空格
    )

    strs = strs.replace("lt正gt", "").strip()  # 特殊需求
    return strs


def ref_clear(str_obj):
    # 为 引文 数据定制的清理
    strs = (
        StringClear(str_obj)
        .None_to_str()  # None 转 空字符串
        .remove_html_tag()  # 清理html标签
        .to_str()  # 防止其他类型传入 比如 int double
        .qj_to_bj()  # 全角转半角
        .strip_quotes()  # 清理 双引号
        .clean_symbols()  # 清理已知的符号
        .collapse_spaces()  # 移除多余空格,连续多个空格变一个
        .lower()  # 小写
        .remove_diacritics()  # 去除音标 转换成字母
        .get_str()  # 获取str
        .strip()  # 去掉空格
    )
    return strs


def clear_obj(str_obj):
    # 为对象化定制的清理
    str_obj = clear_au_organ(str_obj)
    # str_obj = str_obj.replace("ß", "SS") # "ß" 的 大写就是 "SS"
    result = (
        StringClear(str_obj)
        .remove_diacritics()  # 清理音标
        .upper()
        .get_str()  # 获取str
        .strip()  # 去掉空格
    )
    return result


def normalize_title_for_es(title: str):
    _title = StringClear(title).convert_to_simplified().qj_to_bj().get_str()
    has_chinese = re.search(r"[\u4e00-\u9fa5]", _title)
    if not has_chinese:
        _title = re.sub(r"[－—‑–−―-]", " ", _title)
    return _title.strip()
