# 某些业务中的字符串处理 算是特定场景的工具 不算通用工具
import re

from re_common.v2.baselibrary.utils.string_bool import is_all_symbols


def clean_organ_postcode(organ):
    """
    格式化组织名称字符串，移除括号内容并删除独立的6位数字（邮政编码），然后清理标点。

    备注: 该方法替换java 里面的 formatOrgan

    参数:
        organ (str): 输入的组织名称字符串，可能包含括号、分号和邮政编码。

    返回:
        str: 格式化并清理后的组织名称字符串（无独立6位数字）。
    """
    # 如果输入为空，设为空字符串以避免后续操作报错
    if not organ:
        organ = ""

    # 删除方括号和圆括号中的内容（包括括号本身）
    organ = re.sub(r"\[.*?\]", "", organ)  # 非贪婪匹配方括号内容
    organ = re.sub(r"\(.*?\)", "", organ)  # 非贪婪匹配圆括号内容

    # 定义正则表达式，匹配独立的6位数字
    # \b 表示单词边界，确保6位数字是独立的（前后不是字母、数字或下划线）
    organ = re.sub(r"\b[0-9]{6}\b", "", organ)

    # 初始化结果列表，用于存储处理后的组织名称部分
    format_organ = []
    # 按分号分割字符串，生成组织名称的各个部分
    organ_parts = organ.split(";")

    # 遍历每个部分，追加到结果列表
    for temp_organ in organ_parts:
        # 去除首尾多余空格后追加（避免因移除邮编导致的空字符串）
        cleaned_part = temp_organ.strip()
        # 如果首尾是标点符号，则移除
        # 定义标点符号的正则表达式（这里包括常见标点）
        punctuation = r"^[!,.?;:#$%^&*+-]+|[!,.?;:#$%^&*+-]+$"
        cleaned_part = re.sub(punctuation, "", cleaned_part)
        if cleaned_part:  # 只追加非空部分
            format_organ.append(cleaned_part)

    # 用分号连接结果，转换为大写并清理标点
    format_organ = ";".join(format_organ)

    # 返回最终结果并去除首尾空格
    return format_organ.strip()


def get_first_organ(organ):
    if not organ:
        return ""
    organ_list = organ.strip().split(";")
    for organ_one in organ_list:
        # 清理邮政编码
        organ_one = clean_organ_postcode(organ_one)
        if organ_one.strip():
            return organ_one

    return ""


def get_first_author(author: str) -> str:
    if not author:
        return ""
    au_list = author.strip().split(";")
    for au in au_list:
        au = re.sub("\\[.*?]", "", au)
        au = re.sub("\\(.*?\\)", "", au)
        if au.strip():
            return au
    return ""


def get_author_list(author: str):
    lists = []
    if not author:
        return []
    au_list = author.strip().split(";")
    for au in au_list:
        au = re.sub("\\[.*?]", "", au)
        au = re.sub("\\(.*?\\)", "", au)
        if au.strip():
            lists.append(au.strip())
    return lists


def get_scopus_author_abbr(author_row: str):
    if not author_row:
        return ""
    author_list = author_row.split("&&")
    if len(author_list) != 3:
        raise Exception("错误的数据个数 可能来自其他数据源")

    abbr_list = author_list[0].strip().split(";")
    abbr_list = [author.strip() for author in abbr_list if
                 author.strip() and author.strip().lower() not in ("*", "and")]
    return ";".join(abbr_list)


def get_wos_author_abbr(author_row: str):
    if not author_row:
        return ""
    author_list = author_row.split("&&")
    if len(author_list) != 4:
        raise Exception("错误的数据个数 可能来自其他数据源")
    abbr_list = []
    abbr_list_au = author_list[0].strip().split(";")
    abbr_list_ba = author_list[2].strip().split(";")
    abbr_list.extend(abbr_list_au)
    abbr_list.extend(abbr_list_ba)
    abbr_list = [author.strip() for author in abbr_list if
                 author.strip() and author.strip().lower() not in ("*", "and")]
    return ";".join(abbr_list)


def deal_rel_vol(vol_str: str):
    """
    处理 期刊融合时的卷处理逻辑
    """

    # 如果卷是全符号 清理掉
    if is_all_symbols(vol_str):
        vol_str = ""

    if vol_str.replace(".", "").isdigit():
        try:
            float_num = float(vol_str)
            if int(float_num) == float_num:
                return str(int(float_num))
        except:
            pass

    if vol_str.lower().startswith("v "):
        vol_str = vol_str.lower().replace("v ", "").strip()
        return vol_str
    if vol_str.lower().startswith("volume "):
        vol_str = vol_str.lower().replace("volume ", "").strip()
        return vol_str
    if vol_str.lower().startswith("vol. "):
        vol_str = vol_str.lower().replace("vol. ", "").strip()
        return vol_str
    if vol_str.lower().startswith("vol "):
        vol_str = vol_str.lower().replace("vol ", "").strip()
        return vol_str
    return vol_str


def deal_num_strs(input_str):
    """
    int后在str 防止有浮点型的表达方式
    """
    number_list = re.findall(r'\d+', input_str)
    transformed_numbers = [str(int(num)) for num in number_list]

    # 替换原字符串中的数字为转换后的数字
    for num, transformed_num in zip(number_list, transformed_numbers):
        input_str = input_str.replace(num, transformed_num)
    return input_str


def deal_num(num_str):
    """
    将 期格式化 方便 group尤其是有横杆的数据
    该方法 为融合二次分割时使用，如果场景合适也可以用于其他地方
    :param strs:
    :return:
    """
    # 如果期是全符号清理掉
    if is_all_symbols(num_str):
        num_str = ""

    if num_str.lower().startswith("n "):
        num_str = num_str.lower().replace("n ", "").strip()

    num_str = num_str.lower().replace("special_issue_", '').replace("_special_issue", '').replace("issue", "")
    num_str = num_str.replace("spec.", "").replace("iss.", "").replace("spl.", "").replace("special.", "").replace(
        "specialissue.", "")
    num_str = num_str.replace("spec", "").replace("iss", "").replace("spl", "").replace("special", "").replace(
        "specialissue", '')

    num_str = num_str.replace("-", "_").replace(".", "_").upper()
    num_str = num_str.lstrip("_").rstrip("_")
    if num_str.find("_") > -1:
        start, end = num_str.split("_")
        start = deal_num_strs(start)
        end = deal_num_strs(end)
        num_str = start + "_" + end
    else:
        num_str = deal_num_strs(num_str)

    return num_str.lower().strip()
