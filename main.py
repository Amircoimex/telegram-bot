import asyncio
import random
import os
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
concurrent_searches = 5  # تعداد درخواست‌های همزمان

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🚀 شروع ربات با ۵ درخواست همزمان...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False
message_count = 0
active_searches = 0  # تعداد جستجوهای فعال
max_active_searches = concurrent_searches  # حداکثر جستجوهای همزمان

# کلمات کلیدی که نشان می‌دهند جستجو تمام شده
SEARCH_END_KEYWORDS = [
    "⚠️ شماره ای موجود نیست",
    "شماره ای موجود نیست",
    "موجود نیست", 
    "پایان جستجو",
    "تمام شد",
    "نتیجه ای یافت نشد",
    "یافت نشد",
    "لطفا دوباره تلاش کنید"
]

# کلمات کلیدی که نشان می‌دهند جستجو شروع شده
SEARCH_START_KEYWORDS = [
    "ربات در جستجوی شماره",
    "در جستجوی شماره",
    "جستجوی شماره",
    "🔍"
]

# هندلر برای بررسی پیام‌های بات هدف
@app.on_message(filters.chat(target_bot))
async def check_search_status(client, message):
    global active_searches
    
    if not sending:
        return
        
    if message.text:
        message_text_lower = message.text.lower()
        print(f"📨 پیام از بات: {message.text}")
        
        # اگر پیام حاوی کلمات کلیدی پایان جستجو باشد
        if any(keyword in message_text_lower for keyword in [k.lower() for k in SEARCH_END_KEYWORDS]):
            if active_searches > 0:
                active_searches -= 1
            print(f"✅ جستجو تمام شد - جستجوهای فعال: {active_searches}")
            
            # فاصله کوتاه قبل از ارسال درخواست جدید
            delay = random.uniform(0.5, 1.5)
            print(f"⏸️ توقف {delay:.1f} ثانیه...")
            await asyncio.sleep(delay)
        
        # اگر پیام حاوی کلمات کلیدی شروع جستجو باشد (برای لاگ)
        elif any(keyword in message_text_lower for keyword in [k.lower() for k in SEARCH_START_KEYWORDS]):
            print("🔍 جستجو شروع شد...")

# هندلر اصلی برای دستورات کاربر
@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending, message_count, active_searches
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await app.send_message("me", "قبلاً شروع شده ✅")
            return

        sending = True
        message_count = 0
        active_searches = 0
        await app.send_message("me", f"شروع شد ✅ ربات با {concurrent_searches} درخواست همزمان کار می‌کند.")

        # ارسال اولیه ۵ درخواست
        for i in range(concurrent_searches):
            if not sending:
                break
            try:
                await app.send_message(target_bot, message_text)
                message_count += 1
                active_searches += 1
                print(f"📤 پیام #{message_count} به @{target_bot} ارسال شد")
                print(f"🔍 جستجوهای فعال: {active_searches}/{max_active_searches}")
                
                # فاصله کوتاه بین ارسال درخواست‌ها
                delay = random.uniform(0.3, 1.0)
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"❌ خطا در ارسال اولیه: {e}")

        # ادامه کار
        while sending:
            try:
                # اگر تعداد جستجوهای فعال کمتر از حداکثر مجاز باشد
                if active_searches < max_active_searches:
                    # ارسال درخواست جدید
                    await app.send_message(target_bot, message_text)
                    message_count += 1
                    active_searches += 1
                    print(f"📤 پیام #{message_count} به @{target_bot} ارسال شد")
                    print(f"🔍 جستجوهای فعال: {active_searches}/{max_active_searches}")
                    
                    # فاصله کوتاه بین ارسال درخواست‌ها
                    delay = random.uniform(0.3, 1.0)
                    await asyncio.sleep(delay)
                else:
                    # اگر به حداکثر رسیده، صبر کن
                    print(f"⏳ منتظر اتمام یکی از جستجوها... ({active_searches}/{max_active_searches})")
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

    elif text == "وضعیت":
        status = "در حال ارسال ✅" if sending else "متوقف ⏸️"
        await app.send_message("me", f"وضعیت: {status}\nجستجوهای فعال: {active_searches}/{max_active_searches}\nتعداد کل پیام‌ها: {message_count}")

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            active_searches = 0
            await app.send_message("me", f"⛔ ارسال متوقف شد.\nتعداد پیام‌های ارسالی: {message_count}")
        else:
            await app.send_message("me", "هیچ کاری در حال انجام نیست.")

    else:
        await app.send_message("me", "دستور نامعتبر است. از 'شروع' یا 'ایست' استفاده کن.")

print("🤖 ربات با ۵ درخواست همزمان آماده کار است...")
app.run()
