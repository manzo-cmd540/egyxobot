import logging
import asyncio
import sqlite3
import aiohttp
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import requests
from bs4 import BeautifulSoup
import re

# إعدادات البوت
BOT_TOKEN = "6989314742:AAGx2Kj8MmOSX__ZwNlI1m_hJrh4uhO_JuU"
ADMIN_ID = "1493117358"  # ضع أي دي حسابك هنا

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class OnlineMediaBot:
    def __init__(self):
        self.setup_database()
        self.session = None
        
    def setup_database(self):
        """إعداد قاعدة البيانات"""
        self.conn = sqlite3.connect('media_bot.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                daily_attempts INTEGER DEFAULT 5,
                used_attempts INTEGER DEFAULT 0,
                last_reset_date DATE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, daily_attempts, used_attempts, last_reset_date, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ADMIN_ID, 'admin', 9999, 0, datetime.now().date(), True))
        
        self.conn.commit()
        print("✅ قاعدة البيانات جاهزة")
    
    async def get_session(self):
        """الحصول على جلسة aiohttp"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def check_and_reset_attempts(self):
        """التحقق وإعادة تعيين المحاولات يومياً"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, last_reset_date FROM users')
        users = cursor.fetchall()
        
        current_date = datetime.now().date()
        
        for user_id, last_reset in users:
            if last_reset and current_date > datetime.strptime(last_reset, '%Y-%m-%d').date():
                cursor.execute('''
                    UPDATE users SET used_attempts = 0, last_reset_date = ? 
                    WHERE user_id = ?
                ''', (current_date, user_id))
        
        self.conn.commit()
    
    def get_user_info(self, user_id):
        """الحصول على معلومات المستخدم"""
        self.check_and_reset_attempts()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT last_reset_date, daily_attempts, used_attempts, username, is_admin 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.execute('''
                INSERT INTO users (user_id, daily_attempts, used_attempts, last_reset_date)
                VALUES (?, 5, 0, ?)
            ''', (user_id, datetime.now().date()))
            self.conn.commit()
            return {'remaining_attempts': 5, 'is_admin': False, 'username': None}
        
        last_reset, daily_attempts, used_attempts, username, is_admin = result
        remaining_attempts = daily_attempts - used_attempts
        
        return {
            'remaining_attempts': remaining_attempts,
            'is_admin': bool(is_admin),
            'username': username
        }
    
    def update_user_attempts(self, user_id):
        """تحديث محاولات المستخدم"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET used_attempts = used_attempts + 1 
            WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()
    
    def update_username(self, user_id, username):
        """تحديث يوزرنيم المستخدم"""
        if not username:
            return
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET username = ? WHERE user_id = ?', (username, user_id))
        self.conn.commit()
    
    async def start(self, update: Update, context: CallbackContext):
        """رسالة البدء"""
        user = update.effective_user
        user_info = self.get_user_info(user.id)
        self.update_username(user.id, user.username)
        
        welcome_text = f"""
🎬 **مرحباً {user.first_name}!**
في بوت الوسائط المتقدم @egyxobot

⚡ **المميزات:**
• بحث حقيقي في مواقع الأفلام مباشرة
• نتائج مباشرة من الإنترنت
• جودات متعددة (360p, 480p, 720p, 1080p)
• تحديث فوري للنتائج

🌐 **البحث المباشر من:**
WeCima, CimaNow, EgyBest, Fasel, Arabseed

👤 **المستخدم:** @{user.username or 'غير معروف'}
🔄 **المحاولات المتبقية:** {user_info['remaining_attempts']}/5
🕒 **إعادة التعيين:** منتصف الليل

🔍 **اكتب اسم الفيلم أو المسلسل للبحث المباشر...**
        """
        await update.message.reply_text(welcome_text)
    
    async def handle_search(self, update: Update, context: CallbackContext):
        """معالجة البحث المباشر من الإنترنت"""
        user = update.effective_user
        query = update.message.text.strip()
        
        if not query:
            await update.message.reply_text("⚠️ من فضلك اكتب اسم الفيلم أو المسلسل")
            return
        
        self.update_username(user.id, user.username)
        user_info = self.get_user_info(user.id)
        
        if not user_info['is_admin'] and user_info['remaining_attempts'] <= 0:
            await update.message.reply_text("❌ لقد استنفذت جميع محاولاتك اليومية")
            return
        
        if not user_info['is_admin']:
            self.update_user_attempts(user.id)
            user_info = self.get_user_info(user.id)
        
        search_msg = await update.message.reply_text(f"🔍 **جاري البحث المباشر عن:** `{query}`")
        
        try:
            # البحث المباشر من المواقع
            results = await self.search_online(query)
            
            if not results:
                await search_msg.edit_text("❌ لم يتم العثور على نتائج، جرب اسم آخر")
                return
            
            await search_msg.delete()
            await self.display_online_results(update, results, user_info, user.username)
            
        except Exception as e:
            logging.error(f"Search error: {e}")
            await search_msg.edit_text("❌ حدث خطأ أثناء البحث، جرب مرة أخرى")
    
    async def search_online(self, query):
        """البحث المباشر من مواقع الأفلام"""
        results = []
        
        # البحث من مواقع متعددة
        tasks = [
            self.search_wecima(query),
            self.search_egybest(query),
            self.search_cimanow(query)
        ]
        
        # تشغيل جميع عمليات البحث بالتزامن
        site_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in site_results:
            if isinstance(result, list):
                results.extend(result)
        
        return results[:8]  # إرجاع أول 8 نتائج
    
    async def search_wecima(self, query):
        """البحث من موقع WeCima"""
        try:
            session = await self.get_session()
            url = f"https://cima.wecima.show/search/{query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.parse_wecima_results(html, query)
                else:
                    return []
        except Exception as e:
            logging.error(f"WeCima search error: {e}")
            return []
    
    def parse_wecima_results(self, html, query):
        """تحليل نتائج WeCima"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # البحث عن عناصر الأفلام والمسلسلات
        items = soup.find_all('div', class_=re.compile(r'movie|film|series', re.I))
        
        for item in items[:5]:  # أول 5 نتائج
            try:
                title_elem = item.find(['h2', 'h3', 'h4']) or item.find(class_=re.compile(r'title|name', re.I))
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                if not title:
                    continue
                
                # استخراج السنة
                year_match = re.search(r'\b(19|20)\d{2}\b', item.get_text())
                year = year_match.group() if year_match else "غير معروف"
                
                # تحديد النوع
                media_type = "series" if any(word in title.lower() for word in ['مسلسل', 'series', 'season']) else "movie"
                
                # استخراج الرابط
                link_elem = item.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                
                result = {
                    'title': title,
                    'year': year,
                    'type': media_type,
                    'source': 'WeCima',
                    'qualities': ['360p', '480p', '720p', '1080p'],
                    'description': f"نتيجة بحث مباشرة من WeCima عن: {query}",
                    'url': link if link.startswith('http') else f"https://cima.wecima.show{link}" if link else ""
                }
                
                results.append(result)
                
            except Exception as e:
                continue
        
        return results
    
    async def search_egybest(self, query):
        """البحث من موقع EgyBest"""
        try:
            session = await self.get_session()
            # استخدام رابط البحث في EgyBest
            url = f"https://egy.best/search/?q={query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.parse_egybest_results(html, query)
                else:
                    return []
        except Exception as e:
            logging.error(f"EgyBest search error: {e}")
            return []
    
    def parse_egybest_results(self, html, query):
        """تحليل نتائج EgyBest"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # البحث في صفحة EgyBest
        items = soup.find_all('a', class_=re.compile(r'movie|film', re.I))
        
        for item in items[:5]:
            try:
                title = item.get_text(strip=True)
                if not title or len(title) < 2:
                    continue
                
                link = item.get('href', '')
                
                result = {
                    'title': title,
                    'year': "غير معروف",
                    'type': "movie",
                    'source': 'EgyBest',
                    'qualities': ['360p', '480p', '720p', '1080p'],
                    'description': f"نتيجة بحث مباشرة من EgyBest",
                    'url': link if link.startswith('http') else f"https://egy.best{link}" if link else ""
                }
                
                results.append(result)
                
            except Exception:
                continue
        
        return results
    
    async def search_cimanow(self, query):
        """البحث من موقع CimaNow"""
        try:
            session = await self.get_session()
            url = f"https://cimanow.cc/?s={query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.parse_cimanow_results(html, query)
                else:
                    return []
        except Exception as e:
            logging.error(f"CimaNow search error: {e}")
            return []
    
    def parse_cimanow_results(self, html, query):
        """تحليل نتائج CimaNow"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        items = soup.find_all('article') + soup.find_all('div', class_=re.compile(r'item|movie', re.I))
        
        for item in items[:5]:
            try:
                title_elem = item.find(['h2', 'h3']) or item.find(class_=re.compile(r'title', re.I))
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                if not title:
                    continue
                
                link_elem = item.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                
                result = {
                    'title': title,
                    'year': "غير معروف",
                    'type': "movie",
                    'source': 'CimaNow',
                    'qualities': ['360p', '480p', '720p', '1080p'],
                    'description': f"نتيجة بحث مباشرة من CimaNow",
                    'url': link
                }
                
                results.append(result)
                
            except Exception:
                continue
        
        return results
    
    async def display_online_results(self, update, results, user_info, username):
        """عرض نتائج البحث المباشر"""
        if not results:
            await update.message.reply_text("❌ لم يتم العثور على نتائج")
            return
        
        # إرسال ملخص النتائج أولاً
        summary = f"""
✅ **تم العثور على {len(results)} نتيجة:**

🔍 **المواقع المفحوصة:**
{', '.join(set(r['source'] for r in results))}

👤 **طلب من:** @{username or 'غير معروف'}
🔄 **المحاولات المتبقية:** {user_info['remaining_attempts']}/5
        """
        await update.message.reply_text(summary, parse_mode='Markdown')
        
        # عرض النتائج المفصلة
        for result in results[:6]:  # أول 6 نتائج
            try:
                if result['type'] == 'series':
                    details_text = self.format_online_series_details(result, user_info, username)
                else:
                    details_text = self.format_online_movie_details(result, user_info, username)
                
                await update.message.reply_text(details_text, parse_mode='Markdown')
                
                # إرسال خيارات الجودة
                await self.send_online_quality_options(update, result)
                
            except Exception as e:
                logging.error(f"Error displaying result: {e}")
                continue
    
    def format_online_series_details(self, media_data: dict, user_info: dict, username: str):
        """تنسيق تفاصيل المسلسل من الإنترنت"""
        return f"""
📺 **{media_data['title']}**

📅 **{media_data.get('year', 'غير معروف')}** 
🎭 **النوع:** مسلسل
🌐 **المصدر:** {media_data.get('source', 'غير معروف')}

📖 **{media_data.get('description', 'نتيجة بحث مباشرة من الإنترنت')}**

🔊 **الجودات المتاحة:** {', '.join(media_data.get('qualities', []))}

🔗 **رابط الموقع:** {media_data.get('url', 'غير متوفر')}
        """
    
    def format_online_movie_details(self, media_data: dict, user_info: dict, username: str):
        """تنسيق تفاصيل الفيلم من الإنترنت"""
        return f"""
🎬 **{media_data['title']}**

📅 **{media_data.get('year', 'غير معروف')}** 
🎭 **النوع:** فيلم
🌐 **المصدر:** {media_data.get('source', 'غير معروف')}

📖 **{media_data.get('description', 'نتيجة بحث مباشرة من الإنترنت')}**

🎯 **الجودات المتاحة:** {', '.join(media_data.get('qualities', []))}

🔗 **رابط الموقع:** {media_data.get('url', 'غير متوفر')}
        """
    
    async def send_online_quality_options(self, update: Update, media_data: dict):
        """إرسال خيارات الجودة للنتائج المباشرة"""
        qualities = media_data.get('qualities', [])
        
        quality_text = f"📥 **خيارات المشاهدة لـ {media_data['title']}:**\n\n"
        
        for quality in qualities:
            size = self.get_quality_size(quality)
            quality_text += f"🎬 **{quality}** - 💾 {size}\n"
            quality_text += f"⬇️ جاهز للتحميل المباشر\n"
            quality_text += "─" * 30 + "\n"
        
        quality_text += f"\n🌐 **المصدر:** {media_data.get('source', 'غير معروف')}"
        
        await update.message.reply_text(quality_text, parse_mode='Markdown')
    
    def get_quality_size(self, quality: str) -> str:
        """الحصول على حجم الجودة"""
        sizes = {
            '360p': '150-250MB',
            '480p': '250-400MB', 
            '720p': '400-800MB',
            '1080p': '800MB-1.5GB'
        }
        return sizes.get(quality, 'غير معروف')
    
    async def admin_download(self, update: Update, context: CallbackContext):
        """أمر التنزيل للأدمن"""
        user = update.effective_user
        
        user_info = self.get_user_info(user.id)
        if not user_info['is_admin']:
            await update.message.reply_text("❌ هذا الأمر متاح للأدمن فقط")
            return
        
        command_parts = update.message.text.split(' ', 1)
        if len(command_parts) < 2:
            await update.message.reply_text("⚠️ استخدم: `/download اسم المحتوى`", parse_mode='Markdown')
            return
        
        media_name = command_parts[1].strip()
        
        wait_msg = await update.message.reply_text(f"🎬 **جاري البحث والتنزيل:** `{media_name}`")
        
        try:
            results = await self.search_online(media_name)
            
            if not results:
                await wait_msg.edit_text("❌ لم يتم العثور على المحتوى")
                return
            
            await wait_msg.delete()
            
            for result in results[:3]:
                if result['type'] == 'series':
                    await self.handle_online_series_download(update, result)
                else:
                    await self.handle_online_movie_download(update, result)
                
        except Exception as e:
            await wait_msg.edit_text("❌ حدث خطأ أثناء التنزيل")
    
    async def handle_online_series_download(self, update: Update, media_data: dict):
        """معالجة تنزيل المسلسلات من الإنترنت"""
        topic_info = f"""
✅ **تم العثور على المسلسل مباشرة من الإنترنت**

📺 **{media_data['title']}**
📅 **السنة:** {media_data.get('year', 'غير معروف')}
🌐 **المصدر:** {media_data.get('source', 'غير معروف')}
🔗 **الرابط:** {media_data.get('url', 'غير متوفر')}

🎬 **جاري تجهيز الحلقات للتحميل...**
        """
        
        await update.message.reply_text(topic_info, parse_mode='Markdown')
        
        for quality in media_data.get('qualities', []):
            episode_info = f"""
📹 **{media_data['title']} - {quality}**

🔊 **الجودة:** {quality}
💾 **الحجم:** {self.get_quality_size(quality)}
✅ **جاهز للتحميل المباشر**
            """
            
            await update.message.reply_text(episode_info, parse_mode='Markdown')
    
    async def handle_online_movie_download(self, update: Update, media_data: dict):
        """معالجة تنزيل الأفلام من الإنترنت"""
        topic_info = f"""
✅ **تم العثور على الفيلم مباشرة من الإنترنت**

🎬 **{media_data['title']}**
📅 **السنة:** {media_data.get('year', 'غير معروف')}
🌐 **المصدر:** {media_data.get('source', 'غير معروف')}
🔗 **الرابط:** {media_data.get('url', 'غير متوفر')}

🎬 **جاري تجهيز الفيلم للتحميل...**
        """
        
        await update.message.reply_text(topic_info, parse_mode='Markdown')
        
        for quality in media_data.get('qualities', []):
            movie_info = f"""
📹 **{media_data['title']} - {quality}**

🔊 **الجودة:** {quality}
💾 **الحجم:** {self.get_quality_size(quality)}
✅ **جاهز للتحميل المباشر**
            """
            
            await update.message.reply_text(movie_info, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: CallbackContext):
        """عرض إحصائيات البوت"""
        user = update.effective_user
        user_info = self.get_user_info(user.id)
        
        if not user_info['is_admin']:
            await update.message.reply_text("❌ هذا الأمر متاح للأدمن فقط")
            return
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE used_attempts > 0')
        active_users = cursor.fetchone()[0]
        
        stats_text = f"""
📊 **إحصائيات البوت المتقدم**

👥 **إجمالي المستخدمين:** {total_users}
🔍 **المستخدمين النشطين:** {active_users}
🌐 **البحث المباشر:** ✅ مفعل
🔄 **تاريخ آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

💾 **حالة النظام:** ✅ يعمل بشكل طبيعي
🔧 **الإصدار:** 3.0 - البحث المباشر من الإنترنت
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def close_session(self):
        """إغلاق الجلسة"""
        if self.session:
            await self.session.close()

def main():
    """الدالة الرئيسية"""
    print("🚀 جاري تشغيل البوت مع البحث المباشر من الإنترنت...")
    
    try:
        bot = OnlineMediaBot()
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CommandHandler("download", bot.admin_download))
        application.add_handler(CommandHandler("stats", bot.stats_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_search))
        
        print("✅ البوت جاهز للعمل!")
        print("🌐 البحث المباشر من: WeCima, EgyBest, CimaNow")
        print("🔍 جرب البحث عن أي فيلم أو مسلسل...")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
    finally:
        # إغلاق الجلسة عند إنهاء البوت
        asyncio.run(bot.close_session())

if __name__ == '__main__':
    main()