import json
from aiohttp import web
import logging
from lib.config import rclonedir,blrecdir
from lib.file_edit import subdir_get
import lib.rclone as rclone 

logger = logging.getLogger(__name__)





async def handle_webhook(request):  
    try:
        logger.info("正在处理来自BLREC的事件")
        data = await request.read()
        json_data = json.loads(data)
        event_type = json_data.get("type")
        event_data = json_data.get("data")

        logger.info(f"正在处理事件{event_type}")



        match event_type:
            case "PostprocessingCompletedEvent": #后处理完成
                room_id = event_data.get("room_id")
                files = event_data.get("files")
                logger.info(f"视频后处理:完成读取完成,房间ID: {room_id}, 文件列表: {files}")
            
                 # 遍历文件列表并上传每个文件
                for file in files:
                    # 拼接文件路径
                    full_file_path = file
                    # 提取路径 
                    sub_dir = subdir_get(full_file_path, blrecdir)
                    # 拼接云存储路径 将路径补充到
                    cloudbin_path = (f"{rclonedir}{sub_dir}")
                    logger.debug(f"文件 {file} 将上传到{cloudbin_path}")
                    # 上传文件
                    await rclone.upload_file(full_file_path, cloudbin_path)
                    

            case "LiveBeganEvent": 
                logger.debug("开播")

            case "LiveEndedEvent":
                logger.debug("下播")

            case "RoomChangeEvent": 
                logger.debug("直播间信息改变")

            case "RecordingStartedEvent":
                logger.debug("录制开始")

            case "RecordingFinishedEvent":
                logger.debug("录制完成")

            case "RecordingCancelledEvent":
                logger.debug("录制取消")

            case "VideoFileCreatedEvent":
                logger.debug("视频文件创建")
        
            case "VideoFileCompletedEvent":
                logger.debug("视频文件完成")

            case "DanmakuFileCreatedEvent":
                logger.debug("弹幕文件创建")

            case "DanmakuFileCompletedEvent":
                logger.debug("弹幕文件完成")

            case "RawDanmakuFileCreatedEvent":
                logger.debug("原始弹幕文件创建")

            case "RawDanmakuFileCompletedEvent":
                logger.debug("原始弹幕文件完成")

            case "SpaceNoEnoughEvent":
                logger.warning("BLrec提示出现硬盘空间不足")

            case "Error":
                logger.error(f"BLrec提示程序出现异常:{event_data}")
            case _ :
                logger.warning(f"未知的类型{event_type}")
        

    except Exception as e:
        logging.error(f"处理BLREC事件发生错误:{e}")

    logger.debug(f"确认接收到webhook事件{json_data}")


    return web.Response(status=200)