import asyncio
import random
import os
import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

api_id = int(os.environ.get("API_ID", 38528329))
api_hash = os.environ.get("API_HASH", "61564de233d29aff8737fce91232a4e8")
session_string = os.environ.get("SESSION_STRING", "")
target_bot = os.environ.get("TARGET_BOT", "ten_number_bot")
message_text = os.environ.get("MESSAGE_TEXT", "🇹🇳 تونس JONS")

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🤖 ربات راه‌اندازی شد...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False
message_count = 0
cooldown_until = 0
search_timers = {}

# هندلر برای پیام‌های بات هدف
@app.on_message(filters.user(target_bot))
async def handle_bot_messages(client, message):
    global message_count
    
    if not sending:
        return
        
    if message.text:
        print(f"🎯 [{time.strftime('%H:%M:%S')}] از بات: '{message.text}'")
        
        # اگر خطای محدودیت باشه
        if "نمی‌توانید بیش از 5 درخواست همزمان" in message.text:
            print("⏰ محدودیت - توقف ۶۰ ثانیه")
            global cooldown_until
            cooldown_until = time.time() + 60
            return
        
        # اگر جستجو تموم شده (هر پیامی غیر از "جستجوی شماره")
        if "جستجوی شماره" not in message.text:
            print("✅ جستجو تموم شد - ارسال درخواست جدید")
            # ارسال درخواست جدید بعد از ۲ ثانیه
            await asyncio.sleep(2)
            await send_request()

async def send_request():
    """ارسال درخواست جدید"""
    global message_count
    
    if not sending:
        return
        
    try:
        await app.send_message(target_bot, message_text)
        message_count += 1
        print(f"📤 [{time.strftime('%H:%M:%S')}] پیام #{message_count} ارسال شد")
        
        # تایمر برای اتمام خودکار جستجو بعد از ۱۵ ثانیه
        search_id = message_count
        asyncio.create_task(auto_complete_search(search_id))
        
    except FloodWait as e:
        print(f"⏳ FloodWait: {e.value} ثانیه")
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"❌ خطا: {e}")

async def auto_complete_search(search_id):
    """اتمام خودکار جستجو بعد از ۱۵ ثانیه"""
    await asyncio.sleep(15)
    
    if sending:
        print(f"⏰ جستجو #{search_id} خودکار تموم شد - ارسال جدید")
        await send_request()

# هندلر اصلی
@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending, message_count, cooldown_until
    
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await app.send_message("me", "⏳ قبلاً شروع شده!")
            return

        sending = True
        message_count = 0
        cooldown_until = 0
        
        await app.send_message("me", "🚀 ربات شروع به کار کرد!")
        print("🚀 شروع ارسال درخواست‌ها...")

        # شروع با ۵ درخواست اولیه
        for _ in range(5):
            if not sending:
                break
            await send_request()
            await asyncio.sleep(2)  # فاصله ۲ ثانیه بین درخواست‌ها

        # ادامه کار
        while sending:
            try:
                # بررسی کول‌داون
                current_time = time.time()
                if current_time < cooldown_until:
                    remaining = int(cooldown_until - current_time)
                    if remaining % 10 == 0:
                        print(f"⏳ کول‌داون: {remaining} ثانیه")
                    await asyncio.sleep(5)
                    continue
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ خطا: {e}")
                await asyncio.sleep(3)

    elif text == "وضعیت":
        current_time = time.time()
        if current_time < cooldown_until:
            cooldown_status = f"⏰ کول‌داون: {int(cooldown_until - current_time)} ثانیه"
        else:
            cooldown_status = "✅ آماده"
            
        await app.send_message("me",
            f"🟢 در حال اجرا\n"
            f"{cooldown_status}\n"
            f"📤 پیام‌ها: {message_count}"
        )

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            await app.send_message("me", f"⛔ متوقف شد - تعداد پیام‌ها: {message_count}")
        else:
            await app.send_message("me", "🔴 از قبل متوقف است")

    else:
        await app.send_message("me", 
            "🤖 دستورات:\n"
            "├─ شروع - اجرا\n"
            "├─ توقف - توقف\n"
            "└─ وضعیت - وضعیت"
        )

print("🤖 ربات آماده...")
app.run()
