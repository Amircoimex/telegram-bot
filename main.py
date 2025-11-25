import asyncio
import random
import os
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

api_id = int(os.environ.get("API_ID", 38528329))
api_hash = os.environ.get("API_HASH", "61564de233d29aff8737fce91232a4e8")
session_string = os.environ.get("SESSION_STRING", "")
target_bot = os.environ.get("TARGET_BOT", "ten_number_bot")
message_text = os.environ.get("MESSAGE_TEXT", "🇹🇳 تونس JONS")

min_delay = 1
max_delay = 3
concurrent_searches = 5
search_timeout = 10

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🚀 شروع ربات با ۵ درخواست همزمان...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False
message_count = 0
active_searches = 0
max_active_searches = concurrent_searches
cooldown_until = 0  # زمان پایان کول‌داون

# هندلر برای پیام‌های بات هدف
@app.on_message(filters.user(target_bot))
async def check_search_status(client, message):
    global active_searches, cooldown_until
    
    if not sending:
        return
        
    if message.text:
        print(f"🎯 پیام از بات هدف: '{message.text}'")
        
        # اگر خطای محدودیت باشه
        if "نمی‌توانید بیش از 5 درخواست همزمان" in message.text:
            print("⏰ محدودیت بات: توقف ۶۰ ثانیه...")
            cooldown_until = asyncio.get_event_loop().time() + 60  # 60 ثانیه کول‌داون
            return
        
        # هر پیامی از بات هدف (به جز "جستجوی شماره") یعنی جستجو تموم شده
        if "جستجوی شماره" not in message.text:
            if active_searches > 0:
                active_searches -= 1
            print(f"✅ جستجو تمام شد - جستجوهای فعال: {active_searches}")

async def auto_complete_search():
    """اتمام خودکار جستجو بعد از 10 ثانیه"""
    await asyncio.sleep(search_timeout)
    
    global active_searches
    if active_searches > 0:
        active_searches -= 1
        print(f"⏰ جستجو به صورت خودکار تمام شد - جستجوهای فعال: {active_searches}")

# هندلر اصلی
@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending, message_count, active_searches, cooldown_until
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await app.send_message("me", "قبلاً شروع شده ✅")
            return

        sending = True
        message_count = 0
        active_searches = 0
        cooldown_until = 0
        await app.send_message("me", f"شروع شد ✅ ربات با {concurrent_searches} درخواست همزمان کار می‌کند.")

        while sending:
            try:
                # اگر در حالت کول‌داون هستیم
                current_time = asyncio.get_event_loop().time()
                if current_time < cooldown_until:
                    remaining = int(cooldown_until - current_time)
                    print(f"⏳ منتظر پایان کول‌داون: {remaining} ثانیه باقی مانده...")
                    await asyncio.sleep(5)
                    continue
                
                # همیشه ۵ درخواست فعال نگه دار
                while active_searches < max_active_searches and sending:
                    await app.send_message(target_bot, message_text)
                    message_count += 1
                    active_searches += 1
                    print(f"📤 پیام #{message_count} ارسال شد - جستجوهای فعال: {active_searches}/{max_active_searches}")
                    
                    # تایمر برای جستجو
                    asyncio.create_task(auto_complete_search())
                    
                    # **فاصله ۲ ثانیه بین هر درخواست**
                    if active_searches < max_active_searches:  # بعد از آخرین درخواست صبر نکن
                        print("⏸️ توقف ۲ ثانیه بین درخواست‌ها...")
                        await asyncio.sleep(2)
                
                # اگر به ۵ رسیده، صبر کن
                if active_searches >= max_active_searches:
                    print(f"⏳ منتظر اتمام جستجو... ({active_searches}/{max_active_searches})")
                    await asyncio.sleep(2)

            except FloodWait as e:
                print(f"⏳ FloodWait: {e.value} ثانیه")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(3)

    elif text == "وضعیت":
        status = "در حال ارسال ✅" if sending else "متوقف ⏸️"
        current_time = asyncio.get_event_loop().time()
        if current_time < cooldown_until:
            cooldown_status = f"کول‌داون: {int(cooldown_until - current_time)} ثانیه"
        else:
            cooldown_status = "آماده"
        await app.send_message("me", f"وضعیت: {status}\n{cooldown_status}\nجستجوهای فعال: {active_searches}/{max_active_searches}\nتعداد پیام‌ها: {message_count}")

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            active_searches = 0
            cooldown_until = 0
            await app.send_message("me", f"⛔ متوقف شد\nتعداد پیام‌ها: {message_count}")
        else:
            await app.send_message("me", "در حال حاضر فعال نیست")

    else:
        await app.send_message("me", "دستور نامعتبر")

print("🤖 ربات آماده کار است...")
app.run()
