import logging
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.tasks import reset_daily_quotas, cleanup_old_content

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """بدء جدولة المهام"""
    
    # إعادة تعيين الحصة يومياً
    scheduler.add_job(
        reset_daily_quotas,
        'cron',
        hour=0,
        minute=0,
        id='reset_quotas'
    )
    
    # تنظيف المحتوى القديم
    scheduler.add_job(
        cleanup_old_content,
        'cron',
        hour=2,
        minute=0,
        id='cleanup_content'
    )
    
    scheduler.start()
    logger.info("✅ جدولة المهام نشطة")