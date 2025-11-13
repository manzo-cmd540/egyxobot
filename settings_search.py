"""
🎯 الوظيفة: إعدادات البحث
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))


async def show_search_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إعدادات البحث"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ الأدمن فقط")
        return
    
    current_mode = context.user_data.get('search_mode', 'dual')
    
    msg = f"""
⚙️ إعدادات البحث:

🔍 الوضع الحالي: {current_mode}

الخيارات:
1️⃣ البحث المزدوج (Default)
   - البحث في Storage
   - البحث في المواقع
   - عرض كل النتائج

2️⃣ البحث المحلي فقط
   - في المحتوى المحفوظ
   - أسرع
   - بدون الإنترنت

3️⃣ البحث في المواقع فقط
   - في Fasel, Wecima, Eflix
   - أحدث النتائج
   - قد يكون بطيء

الأوامر:
/search_dual - البحث المزدوج
/search_local - البحث المحلي
/search_web - البحث في المواقع
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🔄 مزدوج", callback_data="set_search_dual"),
            InlineKeyboardButton("📦 محلي", callback_data="set_search_local"),
            InlineKeyboardButton("🌐 ويب", callback_data="set_search_web")
        ]
    ]
    
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def set_search_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعيين وضع البحث"""
    
    try:
        query = update.callback_query.data
        
        mode_map = {
            'set_search_dual': ('dual', '🔄 البحث المزدوج'),
            'set_search_local': ('local', '📦 البحث المحلي'),
            'set_search_web': ('web', '🌐 البحث في المواقع')
        }
        
        if query not in mode_map:
            return
        
        mode, mode_name = mode_map[query]
        
        context.user_data['search_mode'] = mode
        
        await update.callback_query.answer(f"✅ {mode_name}")
        
        await update.callback_query.edit_message_text(
            f"✅ تم تعيين الوضع!\n\n"
            f"الوضع الحالي: {mode_name}\n\n"
            f"الآن عند كتابة /search سيتم استخدام هذا الوضع."
        )
        
        logger.info(f"✅ وضع البحث: {mode_name}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")