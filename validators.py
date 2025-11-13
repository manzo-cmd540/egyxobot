import logging
import re

logger = logging.getLogger(__name__)


def validate_phone(phone: str) -> bool:
    """التحقق من صيغة الرقم"""
    
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None


def validate_email(email: str) -> bool:
    """التحقق من صيغة البريد"""
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_group_id(group_id: str) -> bool:
    """التحقق من معرف الجروب"""
    
    try:
        int(group_id)
        return True
    except:
        return False