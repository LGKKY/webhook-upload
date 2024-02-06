import json
import os
from aiohttp import web
import logging
from lib.config import rechimedir,rclonedir
from lib.file_edit import subdir_get
import lib.rclone as rclone 

logger = logging.getLogger(__name__)

async def handle_webhook(request): 
    
    
    try:
        logger.info("正在处理来自录播姬的事件")
        data = await request.read()
        json_data = json.loads(data)
        event_type = json_data.get("EventType")
        event_data = json_data.get("EventData")

        logger.debug(f"正在处理{event_type}")

        username = event_data.get("Name")
        relative_path = event_data.get("RelativePath")

        match event_type:
            case "SessionStarted":
                logging.debug(f"{username}开始录制")

            case "FileOpening":
                logging.debug(f"{username}打开文件")

            case "SessionEnded":
                logging.debug(f"{username}录制结束")

            case "FileClosed":
                logger.info("已经获取到录播姬文件关闭请求，正在处理")
                # 拼接文件完整路径
                full_file_path = os.path.join(rechimedir, relative_path)
                # 提取子路径
                sub_dir = subdir_get(full_file_path, rechimedir)
                # 拼接云端路径
                cloudbin = (rclonedir, sub_dir)

                if os.path.exists(relative_path): 
                    # 处理变量 
                    logger.info(f"获取到{username}关闭文件，尝试上传{relative_path}")
                # 执行命令
                    await rclone.upload_file(full_file_path, cloudbin)
                else:
                    logger.error(f"文件:{relative_path}不存在，无法执行命令",exc_info=True)
    except Exception as e:
        logging.error(f"处理录播姬事件发生错误：{e}")



    logger.debug(f"确认接收到webhook事件{json_data}")
    return web.Response(status=200)

