# -*- coding: utf-8 -*-
# @Time   : 2025/04/01 10:24
# @Author : zip
# @Moto   : Knowledge comes from decomposition
import logging
import os
import sys
from logging.handlers import RotatingFileHandler  # 日志轮转

import colorlog


def set_log(task_name_or_path):
    # 定义日志格式（带颜色 + 无颜色版本）
    colored_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - [%(levelname)8s] - %(module)s.%(funcName)s:%(lineno)d :: %(message)s",
        log_colors={
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    # 无颜色的格式（用于文件输出）
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)8s] - %(module)s.%(funcName)s:%(lineno)d :: %(message)s"
    )

    # 1. 控制台输出 (stdout)
    console_handler = colorlog.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(colored_formatter)
    console_handler.setLevel(logging.INFO)  # 控制台日志级别

    # 2. 文件输出 (roll.log，自动轮转)
    os.makedirs(task_name_or_path, exist_ok=True)
    log_file = os.path.join(task_name_or_path, "roll.log")
    file_handler = RotatingFileHandler(
        filename=log_file,  # 日志文件名
        maxBytes=10 * 1024 * 1024,  # 单个文件最大 10MB
        backupCount=5,  # 保留 3 个备份文件
        encoding="utf-8",  # 避免中文乱码
    )

    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)  # 文件日志级别

    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 全局日志级别

    # 移除默认的 handlers（避免重复输出）
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 添加自定义 handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("日志配置成功：输出到 stdout 和 roll.log")
