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

print("🚀 شروع ربات...")
print(f"🎯 بات هدف: @{target_bot}")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False
message_count = 0

# هندلر برای تمام پیام‌ها از بات هدف
@app.on_message(filters.user(target_bot))
async def handle_bot_messages(client, message):
    print(f"🎯 پیام از بات هدف: '{message.text}'")
    
    global message_count
    if "موجود نیست" in (message.text or ""):
        print("✅ جستجو تمام شد!")
        # تاخیر قبل از ارسال بعدی
        await asyncio.sleep(2)

# هندلر اصلی
@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending, message_count
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await message.reply("قبلاً شروع شده ✅")
            return

        sending = True
        message_count = 0
        await message.reply("شروع شد ✅")

        while sending:
            try:
                # ارسال پیام
                await app.send_message(target_bot, message_text)
                message_count += 1
                print(f"📤 پیام #{message_count} ارسال شد")
                await message.reply(f"📤 پیام #{message_count} ارسال شد")
                
                # منتظر پاسخ بات هدف
                print("⏳ منتظر پاسخ بات هدف...")
                await asyncio.sleep(10)  # ۱۰ ثانیه منتظر پاسخ بمون
                
            except Exception as e:
                print(f"❌ خطا: {e}")
                await asyncio.sleep(3)

    elif text == "توقف":
        sending = False
        await message.reply(f"⛔ متوقف شد - تعداد پیام‌ها: {message_count}")

print("🤖 ربات آماده...")
app.run()
