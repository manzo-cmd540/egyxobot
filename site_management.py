"""
🎯 الوظيفة: إدارة المواقع والبيانات
"""

import logging
import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
DB_PATH = "bot.db"


async def add_site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة موقع جديد"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ الاستخدام: /add_site <name> <url>\n"
            "مثال: /add_site fasel https://faselhd.link"
        )
        return
    
    site_name = context.args[0]
    site_url = context.args[1]
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT UNIQUE,
                site_url TEXT,
                username TEXT,
                password TEXT,
                api_key TEXT,
                image_path TEXT,
                active INTEGER DEFAULT 1,
                added_date DATE,
                updated_date DATE
            )
        """)
        
        c.execute(
            """INSERT OR REPLACE INTO sites 
            (site_name, site_url, active, added_date, updated_date)
            VALUES (?, ?, 1, ?, ?)""",
            (site_name, site_url, datetime.now().date(), datetime.now().date())
        )
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ تم إضافة الموقع: {site_name}\n"
            f"🔗 الرابط: {site_url}\n\n"
            f"الخطوة التالية:\n"
            f"/set_site_user {site_name} <username>\n"
            f"/set_site_pass {site_name} <password>"
        )
        
        logger.info(f"✅ موقع جديد: {site_name}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def set_site_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعيين username"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ الاستخدام: /set_site_user <site_name> <username>"
        )
        return
    
    site_name = context.args[0]
    username = context.args[1]
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            "UPDATE sites SET username = ?, updated_date = ? WHERE site_name = ?",
            (username, datetime.now().date(), site_name)
        )
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ تم تعيين اسم المستخدم\n"
            f"🔐 الموقع: {site_name}\n"
            f"👤 المستخدم: {username}"
        )
        
        logger.info(f"✅ username: {site_name}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def set_site_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعيين password"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ الاستخدام: /set_site_pass <site_name> <password>"
        )
        return
    
    site_name = context.args[0]
    password = context.args[1]
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            "UPDATE sites SET password = ?, updated_date = ? WHERE site_name = ?",
            (password, datetime.now().date(), site_name)
        )
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ تم تعيين كلمة المرور\n"
            f"🔐 الموقع: {site_name}"
        )
        
        logger.info(f"✅ password: {site_name}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def list_sites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المواقع"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            "SELECT site_name, site_url, username, active FROM sites"
        )
        
        sites = c.fetchall()
        conn.close()
        
        if not sites:
            await update.message.reply_text("❌ لا توجد مواقع")
            return
        
        msg = "📋 قائمة المواقع:\n\n"
        
        for idx, (name, url, user, active) in enumerate(sites, 1):
            status = "✅" if active else "❌"
            msg += f"{idx}. {status} {name}\n"
            msg += f"   🔗 {url}\n"
            msg += f"   👤 {user if user else 'لا يوجد'}\n\n"
        
        await update.message.reply_text(msg)
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def handle_site_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رفع صورة للموقع"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    if not update.message.photo:
        await update.message.reply_text("❌ لم أتلقى صورة")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ الاستخدام: ارسل الصورة مع /set_site_image <site_name>"
        )
        return
    
    site_name = context.args[0]
    
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        image_folder = "./site_images"
        os.makedirs(image_folder, exist_ok=True)
        
        image_path = os.path.join(image_folder, f"{site_name}.jpg")
        await file.download_to_drive(image_path)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            "UPDATE sites SET image_path = ? WHERE site_name = ?",
            (image_path, site_name)
        )
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ تم رفع الصورة: {site_name}"
        )
        
        logger.info(f"✅ صورة: {site_name}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")