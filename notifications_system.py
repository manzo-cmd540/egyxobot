"""
🎯 الوظيفة: نشرات الحلقات الجديدة
"""

import logging
import os
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

DB_PATH = "bot.db"


async def subscribe_to_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الاشتراك في نشرات"""
    
    user_id = update.effective_user.id
    