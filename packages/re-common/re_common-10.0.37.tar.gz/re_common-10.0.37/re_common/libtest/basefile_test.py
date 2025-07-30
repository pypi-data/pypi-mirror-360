from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile

# files_line_list = BaseFile.read_end_line(r"F:\db3\mysql_date\test\part-00000", 3)
# for file_line in files_line_list:
#     # file_line = str(file_line, encoding="utf-8")
#     # file_line = file_line.decode(encoding="utf-8")
#     print(file_line)

for file in BaseDir.get_dir_all_files(r"F:\db3\mysql_date\data_dir"):
    files_line_list = BaseFile.read_end_line(r"F:\db3\mysql_date\test\part-00000", 11000)
    strs = "\n".join(files_line_list)
    BaseFile.single_add_file(r"F:\db3\mysql_date\end\part-00000", strs + "\n")

