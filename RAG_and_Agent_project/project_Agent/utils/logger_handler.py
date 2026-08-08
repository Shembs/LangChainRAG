import logging
import os

import datetime

from utils.path_tool import get_abs_path

# 日志保存的路径
LOG_ROOT = get_abs_path("logs")

# 确保日志目录存在
os.makedirs(LOG_ROOT,exist_ok=True)

# 日志的格式
DEFAULT_LOG_FORMAT = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
)

def get_logger(
        name:str = "agent",
        console_level:int = logging.INFO,
        file_level:int = logging.DEBUG,
        log_file = None,
)-> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(console_level)

#     避免重复日志
    if logger.handlers:
        return logger
#     配置日志格式
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

#     文件日志
    if not log_file:
        log_file = os.path.join(LOG_ROOT,f"{name}_{datetime.datetime.now().strftime('%y%m%d')}.log")

    file_handler = logging.FileHandler(log_file,encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger


# 快捷获取日志记录器
logger = get_logger()


if __name__ == '__main__':
    logger.info("这是一条info日志")
    logger.debug("这是一条debug日志")
    logger.error("这是一条error日志")
    logger.warning("这是一条warning日志")

