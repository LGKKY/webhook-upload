
# 由于录播姬的webhook输出的是相对路径，需要补充工作路径
rechimedir = "/home/luopu/record/rechime"

# 由于blrec的webhook是绝对路径，并且没有用户名相关信息，需要补充存放目录

blrecdir = "/home/luopu/record/blrec"

# —————————————rclone设置——————————————
# rclone上传目录 务必加入最后的"/"
rclonedir = "od:测试文件夹/"
# rclone的上传模式 默认为move(移动)
rcmode = "move"
# 请在下面填写rclone的配置文件
rcconf = "C:/Users/kjfg_/AppData/Roaming/rclone/rclone.conf"
# 以下填写rclone主程序路径
rclone = "D:/rclone-v1.65.2-windows-amd64/rclone.exe"