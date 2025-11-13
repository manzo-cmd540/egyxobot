import logging
import os
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
IMAGES_FOLDER = os.getenv("IMAGES_FOLDER", "./images")

Path(IMAGES_FOLDER).mkdir(exist_ok=True)


async def handle_admin_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الأدمن فقط يرسل صور"""
    
    user_id = update.effective_user.id
    
    if user_id != BOT_OWNER_ID:
        await update.message.reply_text(
            "❌ فقط الأدمن يقدر يرسل صور!"
        )
        return
    
    try:
        if not update.message.photo:
            await update.message.reply_text("❌ لم أتلقى صورة")
            return
        
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        image_path = Path(IMAGES_FOLDER) / f"admin_image_{photo.file_id}.jpg"
        await file.download_to_drive(image_path)
        
        logger.info(f"✅ تم تحميل صورة من الأدمن")
        
        # إضافة Watermark
        watermarked = await add_watermark_to_image(str(image_path))
        
        await update.message.reply_text(
            "✅ تم استقبال الصورة\n"
            "🎨 تم إضافة Watermark\n"
            "📤 جاهزة للرفع"
        )
        
        context.user_data['current_image'] = watermarked
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


async def add_watermark_to_image(image_path: str):
    """إضافة watermark للصورة"""
    
    try:
        watermark_text = os.getenv("WATERMARK_TEXT", "@egyxobot")
        
        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # زاوية سفلية
        draw.text(
            (10, img.height - 30),
            watermark_text,
            font=font,
            fill=(255, 255, 255, 255)
        )
        
        # حفظ
        output_path = image_path.replace(".jpg", "_watermarked.jpg")
        img.convert("RGB").save(output_path, quality=90)
        
        logger.info(f"✅ تم إضافة watermark")
        
        return output_path
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return image_path