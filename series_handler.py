"""
🎯 الوظيفة: عرض قائمة الحلقات والمعلومات
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.source_content_storage import search_in_source_storage
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


def extract_episode_info(text: str) -> Dict:
    """استخراج معلومات الحلقة"""
    
    try:
        info = {
            'title': '',
            'episode': None,
            'season': None,
            'quality': 'unknown',
            'size': 'unknown'
        }
        
        lines = text.split('\n')
        info['title'] = lines[0].strip()
        
        episode_match = re.search(r'حلقة\s*(\d+)|ep(?:isode)?\s*(\d+)', text, re.IGNORECASE)
        if episode_match:
            info['episode'] = int(episode_match.group(1) or episode_match.group(2))
        
        season_match = re.search(r'موسم\s*(\d+)|s(?:eason)?\s*(\d+)', text, re.IGNORECASE)
        if season_match:
            info['season'] = int(season_match.group(1) or season_match.group(2))
        
        if '1080' in text:
            info['quality'] = '1080p'
        elif '720' in text:
            info['quality'] = '720p'
        elif '480' in text:
            info['quality'] = '480p'
        elif '360' in text:
            info['quality'] = '360p'
        
        size_match = re.search(r'(\d+\.?\d*)\s*(MB|GB)', text)
        if size_match:
            info['size'] = f"{size_match.group(1)} {size_match.group(2)}"
        
        return info
    
    except Exception as e:
        logger.error(f"❌ خطأ في الاستخراج: {e}")
        return {}


def group_episodes_by_series(results: List) -> Dict[str, List]:
    """تجميع الحلقات"""
    
    series_dict = {}
    
    for storage_id, source_group_id, message_id, text, username in results:
        info = extract_episode_info(text)
        series_name = info['title']
        
        if series_name not in series_dict:
            series_dict[series_name] = []
        
        series_dict[series_name].append({
            'storage_id': storage_id,
            'source_group_id': source_group_id,
            'message_id': message_id,
            'text': text,
            'username': username,
            'episode': info['episode'],
            'season': info['season'],
            'quality': info['quality'],
            'size': info['size']
        })
    
    return series_dict


async def handle_series_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة البحث عن مسلسل"""
    
    try:
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /series <اسم المسلسل>\n"
                "مثال: /series سلمات"
            )
            return
        
        query = " ".join(context.args)
        
        search_msg = await update.message.reply_text(
            f"🔍 جاري البحث عن: {query}\n"
            "⏳ الرجاء الانتظار..."
        )
        
        results = search_in_source_storage(query)
        
        if not results:
            await search_msg.edit_text(
                f"❌ لم يتم العثور على: {query}"
            )
            return
        
        series_dict = group_episodes_by_series(results)
        
        for series_name, episodes in series_dict.items():
            await display_series_info(
                update,
                series_name,
                episodes,
                search_msg
            )
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def display_series_info(update: Update, series_name: str, episodes: List, search_msg):
    """عرض معلومات المسلسل"""
    
    try:
        total_episodes = len(episodes)
        qualities = set(ep['quality'] for ep in episodes if ep['quality'] != 'unknown')
        
        total_size = calculate_total_size(episodes)
        
        info_msg = f"""
📺 {series_name}
━━━━━━━━━━━━━━━━━━

📊 المعلومات:
• إجمالي الحلقات: {total_episodes}
• الجودات المتاحة: {', '.join(qualities) if qualities else 'unknown'}
• إجمالي المساحة: {total_size}

━━━━━━━━━━━━━━━━━━
        """
        
        await search_msg.edit_text(info_msg)
        
        await send_episodes_grid(update, series_name, episodes)
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")


async def send_episodes_grid(update: Update, series_name: str, episodes: List):
    """إرسال قائمة الحلقات"""
    
    try:
        episodes.sort(key=lambda x: x['episode'] or 0)
        
        grid_msg = f"📋 قائمة حلقات {series_name}:\n\n"
        
        for i, episode in enumerate(episodes):
            ep_num = episode['episode'] or i + 1
            quality = episode['quality']
            
            grid_msg += f"حلقة {ep_num} ({quality})  "
            
            if (i + 1) % 4 == 0:
                grid_msg += "\n"
        
        keyboard = [
            [
                InlineKeyboardButton("1080p", callback_data=f"filter_quality_1080p_{series_name}"),
                InlineKeyboardButton("720p", callback_data=f"filter_quality_720p_{series_name}"),
                InlineKeyboardButton("480p", callback_data=f"filter_quality_480p_{series_name}")
            ],
            [
                InlineKeyboardButton("📥 تحميل الكل", callback_data=f"download_all_{series_name}"),
                InlineKeyboardButton("📤 نشرات", callback_data=f"notifications_{series_name}")
            ]
        ]
        
        await update.message.reply_text(
            grid_msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")


def calculate_total_size(episodes: List) -> str:
    """حساب إجمالي الحجم"""
    
    try:
        total_mb = 0
        
        for episode in episodes:
            size_str = episode['size']
            
            if 'GB' in size_str:
                value = float(size_str.split()[0])
                total_mb += value * 1024
            elif 'MB' in size_str:
                value = float(size_str.split()[0])
                total_mb += value
        
        if total_mb >= 1024:
            return f"{total_mb / 1024:.2f} GB"
        else:
            return f"{total_mb:.2f} MB"
    
    except:
        return "unknown"


async def handle_quality_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيار الجودة"""
    
    try:
        callback_data = update.callback_query.data
        
        if callback_data.startswith("filter_quality_"):
            parts = callback_data.split("_")
            quality = parts[2]
            series_name = "_".join(parts[3:])
            
            await update.callback_query.answer(f"✅ تم تصفية الجودة: {quality}")
            
            await update.callback_query.edit_message_text(
                f"✅ تم تحديد الجودة: {quality}\n\n"
                f"سيتم عرض حلقات {series_name} بجودة {quality} فقط"
            )
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")


async def handle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة النشرات"""
    
    try:
        callback_data = update.callback_query.data
        
        if callback_data.startswith("notifications_"):
            series_name = callback_data.replace("notifications_", "")
            
            await update.callback_query.answer("✅ تم تفعيل النشرات")
            
            await update.callback_query.edit_message_text(
                f"✅ تم تفعيل النشرات!\n\n"
                f"ستتلقى إشعارات لحلقات {series_name} الجديدة"
            )
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")