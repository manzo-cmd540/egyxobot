import os
from dotenv import load_dotenv

load_dotenv()


def get_env_var(key: str, default: str = ""):
    """الحصول على متغير البيئة"""
    return os.getenv(key, default)


def set_env_var(key: str, value: str):
    """تعيين متغير البيئة"""
    os.environ[key] = value