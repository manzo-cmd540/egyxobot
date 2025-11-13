import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import os

logger = logging.getLogger(__name__)

SOURCE_GROUPS = os.getenv("SOURCE_GROUPS", "").split(",")
DB_PATH = "bot.db"


async def store_source_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حفظ رسائل جروب المصدر"""
    
    try:
        chat_id = update.effective_chat.id
        message = update.message
        
        # التحقق من أن هذا جروب مصدر
        if str(chat_id) not in [g.strip() for g in SOURCE_GROUPS if g.strip()]:
            return
        
        # لا نحفظ الردود
        if message.reply_to_message:
            return
        
        # استخراج المعلومات
        text = message.text or message.caption or ""
        
        if not text:
            return
        
        # حفظ في قاعدة البيانات
        save_to_source_storage(
            chat_id=chat_id,
            message_id=message.message_id,
            text=text,
            user_id=message.from_user.id,
            username=message.from_user.username or "Unknown"
        )
        
        logger.info(f"✅ تم حفظ رسالة من المصدر: {text[:50]}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في حفظ الرسالة: {e}")


def save_to_source_storage(chat_id: int, message_id: int, text: str, 
                           user_id: int, username: str):
    """حفظ الرسالة في جدول التخزين"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # إنشاء جدول إذا لم يكن موجود
        c.execute("""
            CREATE TABLE IF NOT EXISTS source_storage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_group_id INTEGER,
                message_id INTEGER,
                text TEXT,
                user_id INTEGER,
                username TEXT,
                saved_date DATE,
                views INTEGER DEFAULT 0,
                UNIQUE(source_group_id, message_id)
            )
        """)
        
        c.execute("""
            INSERT OR IGNORE INTO source_storage 
            (source_group_id, message_id, text, user_id, username, saved_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, message_id, text, user_id, username, datetime.now().date()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ تم حفظ الرسالة في التخزين")
        
    except Exception as e:
        logger.error(f"❌ خطأ في الحفظ: {e}")


def search_in_source_storage(query: str):
    """البحث في محتوى جروب المصدر"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # البحث باستخدام LIKE
        search_query = f"%{query}%"
        
        c.execute("""
            SELECT id, source_group_id, message_id, text, username 
            FROM source_storage 
            WHERE text LIKE ? 
            ORDER BY saved_date DESC 
            LIMIT 10
        """, (search_query,))
        
        results = c.fetchall()
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"❌ خطأ في البحث: {e}")
        return []


def get_content_stats():
    """إحصائيات المحتوى المخزن"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM source_storage")
        total = c.fetchone()[0]
        
        c.execute("SELECT SUM(views) FROM source_storage")
        total_views = c.fetchone()[0] or 0
        
        c.execute("""
            SELECT source_group_id, COUNT(*) as count 
            FROM source_storage 
            GROUP BY source_group_id
        """)
        
        groups_stats = c.fetchall()
        
        conn.close()
        
        return {
            'total_items': total,
            'total_views': total_views,
            'groups': groups_stats
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return None