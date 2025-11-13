import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "bot.db"


def init_database():
    """إنشاء جميع الجداول"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # جدول المستخدمين
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            daily_quota INTEGER DEFAULT 5,
            used_quota INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0,
            joined_date DATE,
            last_search DATE
        )
    """)
    
    # جدول المحتوى
    c.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            content_type TEXT,
            quality TEXT,
            episode INTEGER,
            season INTEGER,
            year INTEGER,
            language TEXT,
            description TEXT,
            created_date DATE,
            views INTEGER DEFAULT 0
        )
    """)
    
    # جدول تخزين المصدر
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
    
    # جدول القنوات المطلوبة
    c.execute("""
        CREATE TABLE IF NOT EXISTS required_channels (
            id INTEGER PRIMARY KEY,
            channel_id INTEGER UNIQUE,
            channel_name TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    
    # جدول السجلات
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            user_id INTEGER,
            timestamp DATETIME,
            details TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    logger.info("✅ قاعدة البيانات جاهزة")


def add_user(user_id: int, username: str):
    """إضافة مستخدم"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, username, joined_date) VALUES (?, ?, ?)",
            (user_id, username, datetime.now().date())
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ مستخدم جديد: {username}")
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")


def get_stats():
    """الحصول على الإحصائيات"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM content")
        content = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM source_storage")
        storage = c.fetchone()[0]
        
        conn.close()
        
        return {
            'users': users,
            'content': content,
            'storage': storage
        }
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return None