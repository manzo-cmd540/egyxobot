"""
🎯 الوظيفة: البحث المزدوج (Storage + Web)
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.source_content_storage import search_in_source_storage
from scrapers.advanced_scraper import advanced_scraper
from database.db_manager import add_user
import asyncio

logger = logging.getLogger(__name__)


async def handle_dual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """البحث المزدوج"""
    
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        add_user(user_id, username)
        
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /search <اسم المحتوى>\n"
                "مثال: /search سلمات"
            )
            return
        
        query = " ".join(context.args)
        
        search_msg = await update.message.reply_text(
            f"🔍 جاري البحث عن: {query}\n\n"
            "📦 البحث في المحتوى المحفوظ...\n"
            "⏳ الرجاء الانتظار..."
        )
        
        local_results = search_in_source_storage(query)
        
        logger.info(f"📦 Storage: {len(local_results)} نتائج")
        
        await search_msg.edit_text(
            f"🔍 جاري البحث عن: {query}\n\n"
            "📦 تم البحث في المحتوى المحفوظ ✅\n"
            "🌐 جاري البحث في المواقع...\n"
            "⏳ الرجاء الانتظار..."
        )
        
        web_results = await advanced_scraper.search_all(query)
        
        logger.info(f"🌐 المواقع: {len(web_results)} نتائج")
        
        all_results = {
            'local': local_results,
            'web': web_results
        }
        
        await display_dual_results(
            update, 
            search_msg, 
            query, 
            all_results
        )
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def display_dual_results(update: Update, search_msg, query: str, results: dict):
    """عرض النتائج"""
    
    try:
        local_results = results.get('local', [])
        web_results = results.get('web', [])
        
        if not local_results and not web_results:
            await search_msg.edit_text(
                f"❌ لم يتم العثور على نتائج عن: {query}\n\n"
                "💡 جرّب كلمات أخرى"
            )
            return
        
        response = f"✅ نتائج البحث عن: {query}\n\n"
        
        if local_results:
            response += "📦 من المحتوى المحفوظ:\n"
            response += "━━━━━━━━━━━━━━━━━━\n"
            
            for idx, (storage_id, source_group_id, message_id, text, username) in enumerate(local_results[:5], 1):
                title = text[:50] + "..." if len(text) > 50 else text
                response += f"{idx}. 📺 {title}\n"
                response += f"   👤 {username}\n\n"
        
        if web_results:
            response += "\n🌐 من المواقع:\n"
            response += "━━━━━━━━━━━━━━━━━━\n"
            
            for idx, result in enumerate(web_results[:5], 1):
                response += f"{idx}. 🎬 {result['title']}\n"
                response += f"   📊 الجودة: {result['quality']}\n"
                response += f"   📍 من: {result['source']}\n\n"
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "📦 من المحفوظ فقط",
                    callback_data="search_mode_local"
                ),
                InlineKeyboardButton(
                    "🌐 من المواقع فقط",
                    callback_data="search_mode_web"
                )
            ],
            [
                InlineKeyboardButton(
                    "⚙️ إعدادات البحث",
                    callback_data="search_settings"
                )
            ]
        ]
        
        await search_msg.edit_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    except Exception as e:
        logger.error(f"❌ خطأ في العرض: {e}")


async def handle_search_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيار وضع البحث"""
    
    try:
        query = update.callback_query.data
        
        if query == "search_mode_local":
            mode = "📦 البحث في المحتوى المحفوظ فقط"
            context.user_data['search_mode'] = 'local'
        
        elif query == "search_mode_web":
            mode = "🌐 البحث في المواقع فقط"
            context.user_data['search_mode'] = 'web'
        
        else:
            return
        
        await update.callback_query.answer("✅ تم التحديث")
        
        await update.callback_query.edit_message_text(
            f"✅ تم تحديث الإعداد!\n\n"
            f"الوضع الحالي: {mode}\n\n"
            f"الآن عند البحث سيتم استخدام هذا الوضع فقط."
        )
        
        logger.info(f"✅ تم تغيير وضع البحث: {mode}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")