import logging
import os
from pathlib import Path

LOG_FILE = "bot.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def setup_logger():
    """تعريف نظام السجلات"""
    
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    
    # معالج الملف
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(LOG_LEVEL)
    
    # معالج Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    
    # الصيغة
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_action(action: str, user_id: int, details: str = ""):
    """تسجيل إجراء"""
    logger = logging.getLogger(__name__)
    logger.info(f"{action} | User: {user_id} | {details}")