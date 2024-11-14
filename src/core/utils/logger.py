import logging
import os
import sys

def setup_logger(name: str) -> logging.Logger:
    """设置并返回一个logger实例"""
    logger = logging.getLogger(name)
    
    # 如果logger已经有处理器，直接返回
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 文件处理器
    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'mahjong.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 