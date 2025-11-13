import logging
import os
from dotenv import load_dotenv
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ContextTypes
)
from telegram import Update

# استيراد جميع المعالجات
from handlers.search_from_source import handle_search_request, handle_fetch_button
from handlers.source_content_storage import store_source_message
from handlers.source_admin_commands import (
    show_source_stats, list_source_content, clear_source_storage
)
from handlers.admin_handler import (
    handle_admin_commands, handle_premium_commands,
    handle_settings_commands
)
from handlers.membership_handler import (
    toggle_membership_check, add_required_channel,
    remove_required_channel, list_required_channels
)
from handlers.image_handler import handle_admin_image_upload
from handlers.account_handler import (
    handle_login_account, handle_verify_code, 
    handle_verify_password, show_account_status
)
from database.db_manager import init_database
from utils.logger import setup_logger
from scheduler.scheduler import start_scheduler

load_dotenv()

logger = logging.getLogger(__name__)
setup_logger()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN غير موجود")
    exit(1)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية"""
    await update.message.reply_text(
        """
🤖 مرحباً بك في البوت الذكي!

✨ الميزات:
🔍 ابحث عن أفلام ومسلسلات
📺 محتوى محفوظ من جروب المصدر
📥 تحميل ملفات ضخمة (2GB+)
🎬 تنظيم ذكي للمحتوى

📝 الأوامر:
/search <name> - ابحث عن محتوى
/help - المساعدة
/mylibrary - مكتبتك
        """
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    
    is_admin = update.effective_user.id == BOT_OWNER_ID
    
    help_text = """
📌 أوامر البحث:
/search <name> - ابحث عن محتوى
/mylibrary - محتواك المحفوظ
/recent - آخر محتوى

🎬 محتوى متاح:
• أفلام عربية وأجنبية
• مسلسلات
• أفلام كرتون
• برامج
    """
    
    if is_admin:
        help_text += """

👨‍💼 أوامر الأدمن:
/admin_panel - لوحة التحكم
/source_stats - إحصائيات
/list_storage - المحتوى المحفوظ
/clear_storage <days> - تنظيف قديم

💎 المستخدمين المميزين:
/add_premium <id> [days] - إضافة
/remove_premium <id> - حذف
/list_premium - القائمة

⚙️ الإعدادات:
/settings - الإعدادات الكاملة
        """
    
    await update.message.reply_text(help_text)


async def post_init(application: Application):
    """تهيئة البوت"""
    logger.info("🔄 جاري تهيئة البوت...")
    
    init_database()
    start_scheduler()
    
    logger.info("✅ البوت جاهز للعمل")


def main():
    """البداية"""
    try:
        logger.info("🚀 بدء البوت...")
        
        app = Application.builder().token(BOT_TOKEN).build()
        
        app.post_init = post_init
        
        # ────── أوامر أساسية ──────
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        
        # ────── البحث والتحميل من المصدر ──────
        app.add_handler(CommandHandler("search", handle_search_request))
        app.add_handler(CallbackQueryHandler(handle_fetch_button, pattern="^fetch_"))
        
        # ────── حفظ محتوى المصدر ──────
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            store_source_message
        ))
        
        # ────── أوامر الأدمن ──────
        app.add_handler(CommandHandler("admin_panel", handle_admin_commands))
        app.add_handler(CommandHandler("source_stats", show_source_stats))
        app.add_handler(CommandHandler("list_storage", list_source_content))
        app.add_handler(CommandHandler("clear_storage", clear_source_storage))
        
        # ────── المستخدمين المميزين ──────
        app.add_handler(CommandHandler("add_premium", handle_premium_commands))
        app.add_handler(CommandHandler("remove_premium", handle_premium_commands))
        app.add_handler(CommandHandler("list_premium", handle_premium_commands))
        
        # ────── الإعدادات ──────
        app.add_handler(CommandHandler("settings", handle_settings_commands))
        app.add_handler(CommandHandler("set_quota", handle_settings_commands))
        app.add_handler(CommandHandler("set_watermark", handle_settings_commands))
        
        # ────── التحقق من العضوية ──────
        app.add_handler(CommandHandler("toggle_membership", toggle_membership_check))
        app.add_handler(CommandHandler("add_required_channel", add_required_channel))
        app.add_handler(CommandHandler("remove_required_channel", remove_required_channel))
        app.add_handler(CommandHandler("list_required_channels", list_required_channels))
        
        # ────── الصور (أدمن فقط) ──────
        app.add_handler(MessageHandler(filters.PHOTO, handle_admin_image_upload))
        
        # ────── إدارة الحساب ──────
        app.add_handler(CommandHandler("login_account", handle_login_account))
        app.add_handler(CommandHandler("verify_code", handle_verify_code))
        app.add_handler(CommandHandler("verify_password", handle_verify_password))
        app.add_handler(CommandHandler("account_status", show_account_status))
        
        logger.info("✅ البوت يعمل!")
        app.run_polling(allowed_updates=["message", "callback_query"])
    
    except KeyboardInterrupt:
        logger.info("🛑 توقف البوت")
    except Exception as e:
        logger.error(f"❌ خطأ حرج: {e}")
        raise


if __name__ == "__main__":
    main()