# إعدادات البوت
BOT_TOKEN = "6989314742:AAGx2Kj8MmOSX__ZwNlI1m_hJrh4uhO_JuU"
ADMIN_ID = "1493117358"  # ضع أي دي حسابك هنا

# إعدادات قاعدة البيانات
DATABASE_CONFIG = {
    'name': 'media_bot.db',
    'reset_time': '00:00'  # إعادة التعيين عند منتصف الليل
}

# إعدادات المحاولات
USER_ATTEMPTS_CONFIG = {
    'daily_attempts': 5,
    'admin_attempts': 9999,
    'reset_time': 'daily'  # يومياً بدلاً من كل 24 ساعة
}

# المواقع المدعومة
SUPPORTED_SITES = [
    'wecima', 'fasel', 'cimanow', 'arabseed',
    'egybest', 'akwam', 'shahid4u', 'akherkora'
]