import logging

logger = logging.getLogger(__name__)


def handle_error(error: Exception, context: str = ""):
    """معالجة الأخطاء"""
    
    logger.error(f"❌ خطأ في {context}: {str(error)}")
    
    return {
        'status': 'error',
        'message': str(error),
        'context': context
    }