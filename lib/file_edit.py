import os
def subdir_get(file_path, common_dir):
    """
    提取子目录的方法，输入文件完整路径和根路径，输出提取出来的子路径。
    """
    sub_dir = file_path.replace(common_dir, "", 1)  # 去掉公共子目录部分
    sub_dir = "/".join(sub_dir.split("/")[:-1]) + "/"  # 提取子目录部分
    return sub_dir
