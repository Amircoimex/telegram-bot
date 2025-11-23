import asyncio
import random
import os
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

# دریافت تنظیمات از متغیرهای محیطی
api_id = int(os.environ.get("API_ID", 38528329))
api_hash = os.environ.get("API_HASH", "61564de233d29aff8737fce91232a4e8"))
session_string = os.environ.get("SESSION_STRING", "")
target_bot = os.environ.get("TARGET_BOT", "ten_number_bot")
message_text = os.environ.get("MESSAGE_TEXT", "🇹🇳 تونس DL")

min_delay = 1
max_delay = 3
concurrent_searches = 5

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🚀 شروع ربات با ۵ درخواست همزمان...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False
message_count = 0
active_searches = 0
max_active_searches = concurrent_searches

# هندلر برای بررسی پیام‌های بات هدف
@app.on_message(filters.chat(target_bot))
async def check_search_status(client, message):
    global active_searches
    
    if not sending:
        return
        
    if message.text:
        print(f"🔍 پیام کامل از بات: '{message.text}'")
        
        # تشخیص خودکار پایان جستجو - اگر پیام جدیدی نیست و فقط جستجو شروع شده
        if "جستجوی شماره" in message.text and not "موجود نیست" in message.text:
            print("⏳ جستجو در حال انجام...")
        else:
            # اگر پیام متفاوته، احتمالاً جستجو تموم شده
            if active_searches > 0:
                active_searches -= 1
            print(f"✅ جستجو تمام شد - پیام: '{message.text}'")
            print(f"📊 جستجوهای فعال: {active_searches}")
            
            # فاصله کوتاه
            delay = random.uniform(0.5, 1.5)
            print(f"⏸️ توقف {delay:.1f} ثانیه...")
            await asyncio.sleep(delay)

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

        # ارسال اولیه
        for i in range(concurrent_searches):
            if not sending:
                break
            try:
                await app.send_message(target_bot, message_text)
                message_count += 1
                active_searches += 1
                print(f"📤 پیام #{message_count} ارسال شد - جستجوهای فعال: {active_searches}/{max_active_searches}")
                
                delay = random.uniform(0.3, 1.0)
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"❌ خطا: {e}")

        # ادامه کار
        while sending:
            try:
                if active_searches < max_active_searches:
                    await app.send_message(target_bot, message_text)
                    message_count += 1
                    active_searches += 1
                    print(f"📤 پیام #{message_count} ارسال شد - جستجوهای فعال: {active_searches}/{max_active_searches}")
                    
                    delay = random.uniform(0.3, 1.0)
                    await asyncio.sleep(delay)
                else:
                    print(f"⏳ منتظر اتمام جستجو... ({active_searches}/{max_active_searches})")
                    await asyncio.sleep(3)  # افزایش زمان انتظار

            except FloodWait as e:
                print(f"⏳ FloodWait: {e.value} ثانیه")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(3)

    elif text == "وضعیت":
        status = "در حال ارسال ✅" if sending else "متوقف ⏸️"
        await app.send_message("me", f"وضعیت: {status}\nجستجوهای فعال: {active_searches}/{max_active_searches}\nتعداد پیام‌ها: {message_count}")

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            active_searches = 0
            await app.send_message("me", f"⛔ متوقف شد\nتعداد پیام‌ها: {message_count}")
        else:
            await app.send_message("me", "در حال حاضر فعال نیست")

    else:
        await app.send_message("me", "دستور نامعتبر")

print("🤖 ربات آماده کار است...")
app.run()
