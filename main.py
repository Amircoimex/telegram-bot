import asyncio
import random
import os
import re
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

# دریافت تنظیمات از متغیرهای محیطی
api_id = int(os.environ.get("API_ID", 38528329))
api_hash = os.environ.get("API_HASH", "61564de233d29aff8737fce91232a4e8")
session_string = os.environ.get("SESSION_STRING", "")
target_bot = os.environ.get("TARGET_BOT", "ten_number_bot")
message_text = os.environ.get("MESSAGE_TEXT", "🇹🇳 تونس DL")

min_delay = 1
max_delay = 3

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🚀 شروع ربات هوشمند...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False
message_count = 0
search_in_progress = False

# کلمات کلیدی که نشان می‌دهند جستجو تمام شده
SEARCH_END_KEYWORDS = [
    "شماره ای موجود نیست",
    "موجود نیست", 
    "پایان جستجو",
    "تمام شد",
    "نتیجه ای یافت نشد",
    "یافت نشد"
]

@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending, message_count, search_in_progress
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await app.send_message("me", "قبلاً شروع شده ✅")
            return

        sending = True
        message_count = 0
        search_in_progress = False
        await app.send_message("me", f"شروع شد ✅ ربات منتظر اتمام هر جستجو می‌ماند.")

        while sending:
            try:
                if not search_in_progress:
                    # ارسال پیام جدید فقط وقتی جستجو تمام شده
                    await app.send_message(target_bot, message_text)
                    message_count += 1
                    print(f"📤 پیام #{message_count} به @{target_bot} ارسال شد")
                    search_in_progress = True
                    print("⏳ منتظر اتمام جستجو...")
                
                # منتظر ماندن بین چک‌ها
                await asyncio.sleep(2)

            except FloodWait as e:
                print(f"⏳ FloodWait: توقف {e.value} ثانیه...")
                await asyncio.sleep(e.value)
            except RPCError as e:
                print(f"❌ RPCError: {e}")
                sending = False
                await asyncio.sleep(3)
            except Exception as e:
                print(f"❌ Error: {e}")
                sending = False
                await asyncio.sleep(3)

    # بررسی پیام‌های بات هدف برای تشخیص اتمام جستجو
    @app.on_message(filters.chat(target_bot))
    async def check_search_status(client, message):
        global search_in_progress
        
        if not sending:
            return
            
        message_text_lower = message.text.lower() if message.text else ""
        
        # اگر پیام حاوی کلمات کلیدی پایان جستجو باشد
        if any(keyword in message_text_lower for keyword in [k.lower() for k in SEARCH_END_KEYWORDS]):
            print("✅ جستجو تمام شد - آماده ارسال پیام بعدی")
            search_in_progress = False
            
            # فاصله تصادفی قبل از ارسال پیام جدید
            delay = random.uniform(min_delay, max_delay)
            print(f"⏸️ توقف {delay:.1f} ثانیه قبل از ارسال بعدی...")
            await asyncio.sleep(delay)

    elif text == "وضعیت":
        status = "در حال ارسال ✅" if sending else "متوقف ⏸️"
        search_status = "در حال جستجو 🔍" if search_in_progress else "آماده ارسال ✅"
        await app.send_message("me", f"وضعیت: {status}\nجستجو: {search_status}\nتعداد پیام‌ها: {message_count}")

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            search_in_progress = False
            await app.send_message("me", f"⛔ ارسال متوقف شد.\nتعداد پیام‌های ارسالی: {message_count}")
        else:
            await app.send_message("me", "هیچ کاری در حال انجام نیست.")

    else:
        await app.send_message("me", "دستور نامعتبر است. از 'شروع' یا 'ایست' استفاده کن.")

print("🤖 ربات هوشمند آماده کار است...")
app.run()
