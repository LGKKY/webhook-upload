import os
def subdir_get(file_path, common_dir):
    """
    提取子目录的方法，输入文件完整路径和根路径，输出提取出来的子路径。
    """
    sub_dir = file_path.replace(common_dir, "", 1)  # 去掉公共子目录部分
    sub_dir = "/".join(sub_dir.split("/")[:-1]) + "/"  # 提取子目录部分
    return sub_dir

def convert_to_mp4(input_file):
    """
    转换mp4文件
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File {input_file} not found.")

    output_file = os.path.splitext(input_file)[0] + ".mp4"

    # 使用ffmpeg将输入文件转换为mp4格式
    command = f"ffmpeg -i {input_file} -c copy {output_file}"
    return_code = os.system(command)

    if return_code == 0:
        # 删除源文件
        os.remove(input_file)
        return output_file
    else:
        raise Exception(f"Conversion of {input_file} to MP4 failed.")

# 测试函数
input_file = "input.flv"
try:
    output_file = convert_to_mp4(input_file)
    print(f"File converted successfully. Output file: {output_file}")
except Exception as e:
    print(f"Error converting file: {e}")