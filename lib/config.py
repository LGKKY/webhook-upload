
# 接收webhook的host设置
host = "0.0.0.0"
port = "10801"

# 由于录播姬的webhook输出的是相对路径，需要补充工作路径
rechimedir = "/home/patch/record/rechime"

# 由于blrec的webhook是绝对路径，需要补充存放目录让其上传路径正常识别

blrecdir = "/home/patch/record/blrec"

# —————————————rclone设置——————————————
# rclone上传目录 
rclonedir = "remote:path"
# rclone的上传模式 默认为move(剪切),默认情况下上传失败不会删除源文件
rcmode = "move"
# 请在下面填写rclone的配置文件路径
rcconf = "/rclone/rclone.conf"
# 以下填写rclone主程序路径/shell命令
rclone = "rclone.exe"