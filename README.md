# webhook-upload

适用于 blrec mikufans录播姬 的全自动备份工具

正在初期开发,不保证可用性.


## 部署方式

待编写

## 目前计划

- [X]  录制服务支持

  - [X]  录播姬webhook支持
  - [X]  blrec webhook支持
  - [ ]  更多待添加
- [X]  bililogin支持

  - [X]  检查cookie有效性,自动刷新cookie
  - [X]  同步更改blrec的设置
  - [X]  同步更改录播姬的设置
- [ ]  文件相关

  - [X]  rclone支持
  - [ ]  alist支持
- [X]  程序相关

  - [X]  支持toml配置文件
  - [ ]  支持web页面设置,任务状态监视
  - [ ]  自动清理服务端存储空间，flv文件转换mp4
  - [ ]  程序故障自动报告

## 环境要求

Python 3.10+
ffmpeg 
rclone
