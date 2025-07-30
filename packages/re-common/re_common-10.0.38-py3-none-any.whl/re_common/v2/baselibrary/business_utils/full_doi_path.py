import base64
import hashlib
import os

from re_common.v2.baselibrary.business_utils.baseencodeid import BaseLngid

import os
import base64
import hashlib

"""
DOI-文件路径 转换工具

设计目标：
1. 将任意DOI字符串转换为可逆、稳定的文件路径
2. 提供高效的目录分散方案（65,536个子目录）
3. 支持带文件扩展名的存储
4. 完全可逆转换

工作原理：
1. DOI编码：
   - 使用URL安全的Base64编码（RFC 3548）
   - 移除Base64填充的'='字符
   - 文件名长度 ≈ 原始DOI长度 × 4/3

2. 目录分散：
   - 使用MD5哈希创建两级目录结构
   - 目录层级：/MD5[0:2]/MD5[2:4]/
   - 支持65,536个目录（256×256），每目录约1,525个文件（假设10亿文件）

3. 扩展名处理：
   - 保持原始扩展名不变
   - 解码时自动忽略扩展名

典型转换示例：
DOI: "10.1000/xyz123" -> 路径: "a1/b2/QTMuMTAwMC94eXoxMjM.pdf"
路径: "a1/b2/QTMuMTAwMC94eXoxMjM.pdf" -> DOI: "10.1000/xyz123"
"""

base_lngid = BaseLngid()


# 以后需要启用
def doi_to_path(doi: str, ext: str = "") -> str:
    """
    将 DOI 转换为可逆的存储路径：
    1. 对 DOI 进行 URL 安全的 Base64 编码（可逆）
    2. 生成 DOI 的 MD5 哈希用于目录分散
    3. 目录结构：MD5前2字符/次2字符/
    4. 文件名：Base64编码的DOI + 扩展名

    Args:
        doi: 文件 DOI 标识符
        ext: 文件扩展名（如 '.pdf'）

    Returns:
        相对文件路径（如 'a1/b2/QTMuMTAwMC94eXoxMjM=.pdf'）
    """
    # URL安全的Base64编码（可逆）
    doi_b64 = base64.urlsafe_b64encode(doi.encode("utf-8")).decode("ascii").rstrip("=")

    # 生成MD5哈希用于目录分配
    hash_md5 = hashlib.md5(doi.encode("utf-8")).hexdigest()
    dir_level1 = hash_md5[0:2]
    dir_level2 = hash_md5[2:4]

    return os.path.join(dir_level1, dir_level2, f"{doi_b64}{ext}")


# 以后需要启用
def path_to_doi(path: str) -> str:
    """
    从文件路径反推原始DOI
    Args:
        path: 文件路径（如 'a1/b2/QTMuMTAwMC94eXoxMjM=.pdf'）

    Returns:
        原始DOI字符串
    """
    # 提取文件名并移除扩展名
    filename = os.path.basename(path)
    base_name = os.path.splitext(filename)[0]

    # 补齐Base64填充字符
    padding = 4 - (len(base_name) % 4)
    if padding != 4:  # 不需要补齐
        base_name += "=" * padding

    # Base64解码还原DOI
    return base64.urlsafe_b64decode(base_name.encode("ascii")).decode("utf-8")


def doi_to_dir(doi):
    """生成文件的存储路径和可解码的文件名

    Args:
        doi (str): 文件的唯一DOI标识

    Returns:
        str: 文件相对路径，如 "ab/cd/Base64EncodedFileName"
    """
    # 计算DOI的MD5哈希
    hash_md5 = hashlib.md5(doi.encode('utf-8')).hexdigest().lower()

    # 提取目录层级：前2位作为一级目录，3-4位作为二级目录
    first_dir = hash_md5[0:2].upper()
    second_dir = hash_md5[2:4].upper()

    return first_dir + "/" + second_dir


def get_doi_path(doi, case_insensitive=False):
    # 目前使用
    dir_path = doi_to_dir(doi)
    file_name = base_lngid.getDoiid(doi, case_insensitive=case_insensitive) + ".pdf"
    return dir_path + "/" + file_name
