# 提取子目录
def subdir_get(file_path, common_dir):
    sub_dir = file_path.replace(common_dir, "", 1)  # 去掉公共子目录部分
    sub_dir = "/".join(sub_dir.split("/")[:-1]) + "/"  # 提取子目录部分
    return sub_dir

