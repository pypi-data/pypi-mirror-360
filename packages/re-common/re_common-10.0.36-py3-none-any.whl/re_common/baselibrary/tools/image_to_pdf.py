# coding = UTF-8


# 导入Python标准库
import os
from io import BytesIO

# 导入第三方库
from PIL import Image

# 防止中文乱码
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 支持的图片文件格式
SUPPORT_SUFFIX = ["jpg", "jpeg", "png"]


def pic_to_pdf(image_bytes: bytes) -> bytes:
    """将单个图片转换为单张PDF

    :param image_bytes: 图片的bytes对象
    :return: PDF的bytes对象
    """
    # 将bytes对象转换为BytesIO对象
    image_bytes_io = BytesIO(image_bytes)
    # 从内存中读取图片
    image_object = Image.open(image_bytes_io)
    # 打开内存中的文件用于保存PDF
    with BytesIO() as result_bytes_io:
        # 将图片保存为单张PDF
        image_object.save(result_bytes_io, "PDF", resolution=100.0)
        # 获取内存中的文件
        data = result_bytes_io.getvalue()
    # 返回PDF的bytes对象
    return data


def batch_convert(image_path: str, pdf_path: str) -> None:
    """批量将图片转换为单张PDF

    :param image_path: 图片的文件夹
    :param pdf_path: PDF文件保存的文件夹
    """
    # 遍历文件夹下所有文件
    for root, dirs, files in os.walk(image_path, topdown=False):
        for name in files:
            # 提取文件的后缀名
            file_suffix = os.path.splitext(name)[-1].lstrip(".").lower()
            # 检测该文件格式是否受到支持
            if file_suffix not in SUPPORT_SUFFIX:
                continue
            # 拼接出图片文件的绝对路径
            source_file_path = os.path.join(root, name)
            # 拼接出PDF文件的绝对路径
            target_file_path = os.path.join(pdf_path, f"{os.path.splitext(name)[0]}.pdf")
            # 将图片文件转换为PDF文件
            with open(source_file_path, "rb") as source:
                with open(target_file_path, "wb") as target:
                    target.write(pic_to_pdf(source.read()))


batch_convert(r"C:\Users\Administrator\Desktop\上传\zhuanhuan\20230404\新建文件夹 (5)",r"C:\Users\Administrator\Desktop\上传\zhuanhuan\20230404\pdf")