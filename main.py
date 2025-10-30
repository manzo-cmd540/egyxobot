import sys
# هذا الملف أصبح مشغل بسيط يستدعي main() من media_bot.py
try:
    from media_bot import main as run_bot
except Exception as e:
    print(f"❌ لم أتمكن من استيراد media_bot: {e}")
    sys.exit(1)

if __name__ == '__main__':
    try:
        run_bot()
    except KeyboardInterrupt:
        print("🛑 تم إيقاف البوت يدوياً")
        sys.exit(0)