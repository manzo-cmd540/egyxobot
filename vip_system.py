"""
🎯 الوظيفة: نظام المستخدمين المميزين
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
DB_PATH = "bot.db"


async def add_vip_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة VIP"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ الاستخدام: /add_vip <user_id> [days]\n"
            "مثال: /add_vip 123456789 30"
        )
        return
    
    target_id = int(context.args[0])
    days = int(context.args[1]) if len(context.args) > 1 else None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS vip_users (
                user_id INTEGER PRIMARY KEY,
                vip_level TEXT DEFAULT 'normal',
                unlimited_attempts INTEGER DEFAULT 0,
                vip_since DATE,
                vip_until DATE,
                requests_count INTEGER DEFAULT 0,
                last_request_time DATETIME
            )
        """)
        
        if days:
            vip_until = (datetime.now() + timedelta(days=days)).date()
            c.execute(
                """INSERT OR REPLACE INTO vip_users 
                (user_id, vip_level, unlimited_attempts, vip_since, vip_until)
                VALUES (?, 'premium', 0, ?, ?)""",
                (target_id, datetime.now().date(), vip_until)
            )
            until_msg = f"حتى: {vip_until}"
        else:
            c.execute(
                """INSERT OR REPLACE INTO vip_users 
                (user_id, vip_level, unlimited_attempts, vip_since)
                VALUES (?, 'lifetime', 0, ?)""",
                (target_id, datetime.now().date())
            )
            until_msg = "مدى الحياة"
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ تم إضافة VIP!\n"
            f"👤 المستخدم: {target_id}\n"
            f"💎 المستوى: VIP\n"
            f"⏰ {until_msg}"
        )
        
        logger.info(f"✅ VIP: {target_id}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def check_vip_status(user_id: int) -> dict:
    """التحقق من VIP"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            "SELECT vip_level, unlimited_attempts, vip_until FROM vip_users WHERE user_id = ?",
            (user_id,)
        )
        
        result = c.fetchone()
        conn.close()
        
        if result:
            vip_level, unlimited, vip_until = result
            
            if vip_until and datetime.strptime(str(vip_until), "%Y-%m-%d").date() < datetime.now().date():
                return {'status': 'expired', 'level': vip_level}
            
            return {
                'status': 'active',
                'level': vip_level,
                'unlimited': unlimited,
                'until': vip_until
            }
        
        return {'status': 'normal'}
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return {'status': 'normal'}


async def handle_vip_request(update: Update, context: ContextTypes.DEFAULT_TYPE, request_type: str = "download"):
    """معالجة طلب VIP"""
    
    user_id = update.effective_user.id
    
    try:
        vip_status = await check_vip_status(user_id)
        
        if vip_status['status'] == 'active':
            return True
        
        elif vip_status['status'] == 'normal':
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute(
                "SELECT last_request_time FROM vip_users WHERE user_id = ?",
                (user_id,)
            )
            
            result = c.fetchone()
            conn.close()
            
            if result:
                last_request = datetime.fromisoformat(result[0])
                time_diff = datetime.now() - last_request
                
                if time_diff < timedelta(hours=5):
                    remaining_time = timedelta(hours=5) - time_diff
                    hours = remaining_time.seconds // 3600
                    minutes = (remaining_time.seconds % 3600) // 60
                    
                    await update.message.reply_text(
                        f"⏳ الحد الأقصى وصل\n\n"
                        f"الوقت المتبقي: {hours}س {minutes}د\n\n"
                        f"💎 للحصول على VIP:\n"
                        f"/vip_info"
                    )
                    
                    return False
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute(
                "UPDATE vip_users SET last_request_time = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user_id)
            )
            
            conn.commit()
            conn.close()
            
            return True
        
        else:
            return True
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return True


async def show_vip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات VIP"""
    
    keyboard = [
        [
            InlineKeyboardButton("💎 شهري", callback_data="vip_monthly"),
            InlineKeyboardButton("💎💎 سنوي", callback_data="vip_yearly")
        ],
        [
            InlineKeyboardButton("💎💎💎 مدى الحياة", callback_data="vip_lifetime")
        ]
    ]
    
    msg = """
💎 خطط VIP:

🔓 العادي (مجاني):
   • 5 محاولات يومية
   • انتظار 5 ساعات
   • محتوى محدود

💎 VIP شهري:
   • غير محدود
   • بدون انتظار
   • أولوية عالية

💎💎 VIP سنوي:
   • كل المميزات
   • توفير 30%
   • دعم أولوية

💎💎💎 مدى الحياة:
   • كل المميزات
   • بدون تحديثات
   • دعم 24/7
    """
    
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_vip_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة VIP"""
    
    user_id = update.effective_user.id
    
    try:
        vip_status = await check_vip_status(user_id)
        
        if vip_status['status'] == 'active':
            msg = f"""
✅ حالتك: VIP 💎

📊 المعلومات:
• المستوى: {vip_status['level']}
• الصلاحية: {vip_status['until'] or 'مدى الحياة'}
• المحاولات: غير محدودة
• الأولوية: عالية
            """
        else:
            msg = f"""
❌ حالتك: عادي

📊 المعلومات:
• المستوى: عادي
• المحاولات: 5 يومياً
• الانتظار: 5 ساعات

/vip_info
            """
        
        await update.message.reply_text(msg)
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")