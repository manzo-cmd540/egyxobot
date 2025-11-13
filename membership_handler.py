import logging
import os
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv, set_key
from pathlib import Path

logger = logging.getLogger(__name__)
load_dotenv()

ENV_FILE = Path(".env")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
DB_PATH = "bot.db"


async def toggle_membership_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل/تعطيل التحقق من العضوية"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    current = os.getenv("REQUIRE_MEMBERSHIP", "true") == "true"
    new_value = "false" if current else "true"
    
    set_key(str(ENV_FILE), "REQUIRE_MEMBERSHIP", new_value)
    os.environ["REQUIRE_MEMBERSHIP"] = new_value
    
    status = "✅ مفعل" if new_value == "true" else "❌ معطل"
    
    await update.message.reply_text(
        f"✅ تم التحديث\n"
        f"التحقق من العضوية: {status}"
    )
    
    logger.info(f"✅ التحقق من العضوية: {status}")


async def add_required_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة قناة للتحقق"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ الاستخدام: /add_required_channel <id> <name>\n"
            "مثال: /add_required_channel -1001234567890 قناة_الأفلام"
        )
        return
    
    channel_id = int(context.args[0])
    channel_name = " ".join(context.args[1:])
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS required_channels (
            id INTEGER PRIMARY KEY,
            channel_id INTEGER UNIQUE,
            channel_name TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    
    c.execute(
        "INSERT OR REPLACE INTO required_channels (channel_id, channel_name, active) VALUES (?, ?, 1)",
        (channel_id, channel_name)
    )
    
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        f"✅ تم إضافة القناة\n"
        f"📱 المعرف: {channel_id}\n"
        f"📝 الاسم: {channel_name}"
    )
    
    logger.info(f"✅ تم إضافة قناة: {channel_name}")


async def remove_required_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف قناة من التحقق"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    if not context.args:
        await update.message.reply_text("❌ الاستخدام: /remove_required_channel <id>")
        return
    
    channel_id = int(context.args[0])
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("DELETE FROM required_channels WHERE channel_id = ?", (channel_id,))
    
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        f"✅ تم حذف القناة\n"
        f"📱 المعرف: {channel_id}"
    )
    
    logger.info(f"✅ تم حذف قناة {channel_id}")


async def list_required_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض القنوات المطلوبة"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT channel_id, channel_name FROM required_channels WHERE active = 1")
    channels = c.fetchall()
    conn.close()
    
    if not channels:
        await update.message.reply_text("❌ لا توجد قنوات مطلوبة")
        return
    
    check_enabled = os.getenv("REQUIRE_MEMBERSHIP", "true") == "true"
    status = "✅ مفعل" if check_enabled else "❌ معطل"
    
    msg = f"📋 القنوات والمجموعات المطلوبة:\n"
    msg += f"التحقق من العضوية: {status}\n\n"
    
    for idx, (cid, name) in enumerate(channels, 1):
        msg += f"{idx}. {name}\n"
        msg += f"   📱 المعرف: {cid}\n\n"
    
    await update.message.reply_text(msg)