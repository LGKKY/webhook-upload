# 由于录播姬webhook输出的是相对路径，需要补充工作路径
workdir = "D:\Downloads"
# rclone上传目录 务必加入最后的"/"
rclonedir = "od:测试文件夹/"
# rclone的上传模式 默认为move(移动)
rcmode = "move"
# 请在下面填写rclone的配置文件路径
rcconf ="C:/Users/kjfg_/AppData/Roaming/rclone/rclone.conf"
rclone = "D:/rclone-v1.65.2-windows-amd64/rclone.exe"