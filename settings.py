import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """الإعدادات"""
    
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")
    
    BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
    ACCOUNT_PHONE = os.getenv("ACCOUNT_PHONE")
    
    SOURCE_GROUPS = os.getenv("SOURCE_GROUPS", "").split(",")
    TARGET_GROUPS = os.getenv("TARGET_GROUPS", "").split(",")
    
    DEFAULT_QUOTA = int(os.getenv("DEFAULT_DAILY_QUOTA", 5))
    WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "@egyxobot")
    
    TIMEZONE = os.getenv("TIMEZONE", "Africa/Cairo")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")