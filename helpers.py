import logging

logger = logging.getLogger(__name__)


def get_user_mention(username: str, user_id: int) -> str:
    """الحصول على ذكر المستخدم"""
    if username:
        return f"@{username}"
    return f"User {user_id}"


def truncate_text(text: str, length: int = 100) -> str:
    """قص النص"""
    if len(text) > length:
        return text[:length] + "..."
    return text