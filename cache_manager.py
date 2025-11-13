import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """إدارة التخزين المؤقت"""
    
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def set(self, key: str, value, ttl: int = 3600):
        """حفظ في التخزين"""
        self.cache[key] = value
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl)
        logger.info(f"✅ تخزين: {key}")
    
    def get(self, key: str):
        """الحصول من التخزين"""
        if key in self.cache:
            if datetime.now() < self.expiry[key]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.expiry[key]
        
        return None
    
    def clear(self):
        """تنظيف التخزين"""
        self.cache.clear()
        self.expiry.clear()
        logger.info("✅ تم تنظيف التخزين")


cache_manager = CacheManager()