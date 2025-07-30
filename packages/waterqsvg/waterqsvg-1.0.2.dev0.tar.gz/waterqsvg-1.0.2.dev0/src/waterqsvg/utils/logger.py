#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志配置模块
提供统一的日志配置功能
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, Union

def setup_logging(
    level: Union[str, int] = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    log_dir: Optional[Union[str, Path]] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        log_dir: 日志目录路径
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的日志文件数量
        format_string: 自定义格式字符串
        console_output: 是否输出到控制台
        
    Returns:
        配置好的logger对象
    """
    # 转换日志级别
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # 获取根logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 清除现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 设置日志格式
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    formatter = logging.Formatter(format_string)
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file or log_dir:
        if log_dir and not log_file:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "svg_generator.log"
        
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用RotatingFileHandler实现日志轮转
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    _setup_third_party_loggers()
    
    logger.info("日志系统初始化完成")
    return logger

def _setup_third_party_loggers():
    """设置第三方库的日志级别"""
    # 降低matplotlib的日志级别
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    # 降低requests的日志级别
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # 降低其他常见库的日志级别
    logging.getLogger('chardet').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger
    
    Args:
        name: logger名称
        
    Returns:
        logger对象
    """
    return logging.getLogger(name)

def set_log_level(level: Union[str, int]):
    """
    设置日志级别
    
    Args:
        level: 日志级别
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    logging.getLogger().setLevel(level)
    
    # 同时设置所有处理器的级别
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)

def add_file_handler(
    log_file: Union[str, Path],
    level: Union[str, int] = "INFO",
    format_string: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
):
    """
    添加文件处理器
    
    Args:
        log_file: 日志文件路径
        level: 日志级别
        format_string: 格式字符串
        max_bytes: 文件最大大小
        backup_count: 备份文件数量
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter(format_string)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    logging.getLogger().addHandler(file_handler)

def remove_all_handlers():
    """移除所有日志处理器"""
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

class LogContextManager:
    """日志上下文管理器"""
    
    def __init__(self, log_file: Union[str, Path], level: str = "INFO"):
        self.log_file = log_file
        self.level = level
        self.original_handlers = []
    
    def __enter__(self):
        # 保存当前处理器
        logger = logging.getLogger()
        self.original_handlers = logger.handlers[:]
        
        # 添加临时文件处理器
        add_file_handler(self.log_file, self.level)
        
        return logging.getLogger()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 恢复原始处理器
        logger = logging.getLogger()
        
        # 移除所有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 恢复原始处理器
        for handler in self.original_handlers:
            logger.addHandler(handler)