import logging
from telegram import Update
from telegram.ext import ContextTypes
from handlers.source_content_storage import search_in_source_storage
from database.db_manager import add_user
from file_manager import file_manager
import os

logger = logging.getLogger(__name__)


async def handle_search_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة طلب البحث عن محتوى"""
    
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # إضافة المستخدم
        add_user(user_id, username)
        
        # الحصول على الكلمة المفتاحية
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /search <اسم المحتوى>\n"
                "مثال: /search أسد الصحراء"
            )
            return
        
        query = " ".join(context.args)
        
        await update.message.reply_text(
            f"🔍 جاري البحث عن: {query}\n"
            "⏳ الرجاء الانتظار..."
        )
        
        # البحث في المصدر المحفوظ
        results = search_in_source_storage(query)
        
        if not results:
            await update.message.reply_text(
                f"❌ لم يتم العثور على: {query}\n\n"
                "💡 جرّب كلمات أخرى"
            )
            return
        
        # عرض النتائج
        response = f"✅ وجدت {len(results)} نتيجة عن: {query}\n\n"
        
        for idx, (storage_id, source_group_id, message_id, text, username) in enumerate(results[:10], 1):
            title = text[:50] + "..." if len(text) > 50 else text
            
            response += f"{idx}. 📺 {title}\n"
            response += f"   👤 من: @{username}\n\n"
        
        # إرسال النتائج
        await update.message.reply_text(response)
        
        # إرسال أزرار للتحميل
        for idx, (storage_id, source_group_id, message_id, text, username) in enumerate(results[:5], 1):
            button = [[{
                "text": f"📥 احصل على النتيجة {idx}",
                "callback_data": f"fetch_{source_group_id}_{message_id}"
            }]]
            
            await update.message.reply_text(
                f"النتيجة {idx}:",
                reply_markup={"inline_keyboard": button}
            )
        
        logger.info(f"✅ بحث من {username}: {query} - {len(results)} نتائج")
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def handle_fetch_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة زر التحميل"""
    
    try:
        callback_data = update.callback_query.data
        user_id = update.effective_user.id
        
        # استخراج البيانات
        parts = callback_data.split("_")
        source_group_id = int(parts[1])
        message_id = int(parts[2])
        
        await update.callback_query.answer("⏳ جاري التحضير...")
        
        await update.callback_query.edit_message_text(
            "📤 جاري الإرسال من المصدر...\n"
            "الرجاء الانتظار"
        )
        
        # إعادة توجيه الرسالة من المصدر
        if file_manager.is_connected:
            await context.bot.forward_message(
                chat_id=user_id,
                from_chat_id=source_group_id,
                message_id=message_id
            )
            
            await update.callback_query.edit_message_text(
                "✅ تم إرسال الملف بنجاح!\n\n"
                "🎉 استمتع بالمشاهدة"
            )
            
            logger.info(f"✅ تم إرسال ملف للمستخدم {user_id}")
        else:
            await update.callback_query.edit_message_text(
                "❌ الحساب غير متصل حالياً\n"
                "الرجاء محاولة لاحقاً"
            )
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.callback_query.answer(f"❌ خطأ: {str(e)}", show_alert=True)