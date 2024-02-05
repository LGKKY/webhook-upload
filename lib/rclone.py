import asyncio
import logging
from lib.config import rcmode, rcconf,rclone



logger = logging.getLogger(__name__)

async def upload_file(upload: str, cloudbin: str):
    logger.info(f"尝试上传 {upload}")
    try:
        # 创建上传命令
        upload_args = [f"{rclone}", "--config", rcconf, rcmode, f"{upload}",f"{cloudbin}"]
        logger.debug(f"{upload_args}")

        # 执行命令
        process = await asyncio.create_subprocess_exec(
            *upload_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # 获取命令的输出和错误流
        stdout, stderr = await process.communicate()

        # 记录命令的输出
        if stdout:
            logger.debug(f"命令输出: {stdout.decode('utf-8')}")
        
        # 检查命令的返回码
        if process.returncode == 0:
            logger.info(f"{upload} 上传成功")
        else:
            error_message = stderr.decode('utf-8') if stderr else "未知错误"
            logger.error(f"{upload} 上传失败: {error_message}")

    except asyncio.CancelledError:
        logger.warning(f"上传 {upload} 被取消")
    except Exception as e:
        logger.exception(f"上传 {upload} 时出错: {e}")
        # 可能需要进一步处理异常，比如重试或者记录失败的文件等操作
        # 这里的 return 可能需要根据实际情况调整

    return
