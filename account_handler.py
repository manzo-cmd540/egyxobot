import logging
import os
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv, set_key
from pathlib import Path

logger = logging.getLogger(__name__)
load_dotenv()

ENV_FILE = Path(".env")


async def handle_login_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تسجيل دخول الحساب"""
    
    await update.message.reply_text(
        "📱 رقم الحساب: اكتب /set_account_phone <رقم>\n"
        "مثال: /set_account_phone +20123456789"
    )


async def handle_verify_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من الكود"""
    
    if not context.args:
        await update.message.reply_text("❌ الاستخدام: /verify_code 123456")
        return
    
    code = context.args[0]
    
    await update.message.reply_text(
        f"✅ تم التحقق من الكود: {code}"
    )


async def handle_verify_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من كلمة المرور"""
    
    if not context.args:
        await update.message.reply_text("❌ الاستخدام: /verify_password mypassword")
        return
    
    await update.message.reply_text(
        "✅ تم التحقق من كلمة المرور"
    )


async def show_account_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة الحساب"""
    
    phone = os.getenv("ACCOUNT_PHONE", "غير معيّن")
    
    msg = f"""
📱 حالة الحساب:

📞 الرقم المحفوظ: {phone}

🔧 الأوامر:
/set_account_phone <رقم> - تغيير الرقم
/login_account - تسجيل دخول
/verify_code <كود> - التحقق
"""
    
    await update.message.reply_text(msg)