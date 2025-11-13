import logging
from telegram import Update
from telegram.ext import ContextTypes
from handlers.source_content_storage import get_content_stats
import os
import sqlite3

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
DB_PATH = "bot.db"


async def show_source_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات المصدر"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    try:
        stats = get_content_stats()
        
        msg = f"""
📊 إحصائيات المحتوى المحفوظ:

📦 إجمالي المحتوى: {stats['total_items']}
👁️ إجمالي المشاهدات: {stats['total_views']}

📁 توزيع على الجروبات:
"""
        
        for group_id, count in stats['groups']:
            msg += f"   • الجروب {group_id}: {count} محتوى\n"
        
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def list_source_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المحتوى المحفوظ"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, text, username, views, saved_date 
            FROM source_storage 
            ORDER BY saved_date DESC 
            LIMIT 20
        """)
        
        items = c.fetchall()
        conn.close()
        
        if not items:
            await update.message.reply_text("❌ لا يوجد محتوى محفوظ")
            return
        
        msg = "📋 آخر 20 محتوى محفوظ:\n\n"
        
        for idx, (item_id, text, username, views, date) in enumerate(items, 1):
            title = text[:40] + "..." if len(text) > 40 else text
            msg += f"{idx}. {title}\n"
            msg += f"   👤 {username} | 👁️ {views} | 📅 {date}\n\n"
        
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def clear_source_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف المحتوى القديم"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    try:
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /clear_storage <أيام>\n"
                "مثال: /clear_storage 30\n"
                "(سيحذف المحتوى الأقدم من 30 يوم)"
            )
            return
        
        days = int(context.args[0])
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            DELETE FROM source_storage 
            WHERE date('now', '-' || ? || ' days') >= saved_date
        """, (days,))
        
        deleted = c.rowcount
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ تم حذف {deleted} محتوى قديم"
        )
        
        logger.info(f"✅ تم حذف {deleted} محتوى")
        
    except ValueError:
        await update.message.reply_text("❌ أدخل رقم صحيح للأيام")
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")