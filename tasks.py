import logging
import sqlite3
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DB_PATH = "bot.db"


def reset_daily_quotas():
    """إعادة تعيين الحصة اليومية"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("UPDATE users SET used_quota = 0")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ تم إعادة تعيين الحصة اليومية")
    
    except Exception as e:
        logger.error(f"❌ خطأ في إعادة التعيين: {e}")


def cleanup_old_content():
    """تنظيف المحتوى القديم"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # حذف المحتوى الأقدم من 30 يوم
        date_limit = (datetime.now() - timedelta(days=30)).date()
        
        c.execute("DELETE FROM source_storage WHERE saved_date < ?", (date_limit,))
        
        deleted = c.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ تم حذف {deleted} محتوى قديم")
    
    except Exception as e:
        logger.error(f"❌ خطأ في التنظيف: {e}")