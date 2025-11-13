"""
🎯 الوظيفة: إدارة رفع الملفات الكبيرة
- رفع ملفات 2GB+
- استخدام Telethon
- إدارة الاتصال
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./temp")

Path(TEMP_FOLDER).mkdir(exist_ok=True)


class FileManager:
    """إدارة الملفات والرفع"""
    
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    async def connect(self):
        """الاتصال بـ Telethon"""
        try:
            logger.info("🔄 جاري الاتصال...")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال: {e}")
            return False
    
    async def upload_file(self, chat_id, file_path, caption="", progress_callback=None):
        """رفع ملف"""
        
        if not self.is_connected or not self.client:
            logger.error("❌ الحساب غير متصل")
            return None
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ الملف غير موجود: {file_path}")
                return None
            
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            logger.info(f"📤 جاري رفع: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)")
            
            message = await self.client.send_file(
                chat_id,
                file_path,
                caption=caption,
                progress_callback=progress_callback,
                force_document=False
            )
            
            logger.info(f"✅ تم الرفع")
            return message
        
        except Exception as e:
            logger.error(f"❌ خطأ: {e}")
            return None
    
    async def disconnect(self):
        """قطع الاتصال"""
        if self.client:
            await self.client.disconnect()
            self.is_connected = False
            logger.info("🛑 تم قطع الاتصال")


# متغير عام للاستخدام
file_manager = FileManager()