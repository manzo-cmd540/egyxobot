import logging

logger = logging.getLogger(__name__)


def format_message(title: str, data: dict) -> str:
    """تنسيق الرسائل"""
    
    msg = f"📺 {title}\n\n"
    
    for key, value in data.items():
        msg += f"• {key}: {value}\n"
    
    return msg


def format_error(error: str) -> str:
    """تنسيق رسائل الخطأ"""
    return f"❌ {error}"


def format_success(message: str) -> str:
    """تنسيق رسائل النجاح"""
    return f"✅ {message}"