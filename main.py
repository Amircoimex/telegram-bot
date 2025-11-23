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
message_text = os.environ.get("MESSAGE_TEXT", "🇹🇳 تونس JONS")

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🚀 ربات راه اندازی شد...")
print("📱 منتظر دستور 'شروع' از Saved Messages...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False

@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await message.reply("❌ قبلاً شروع شده!")
            return

        sending = True
        await message.reply("✅ ربات شروع به کار کرد!")
        
        count = 0
        while sending and count < 5:  # فقط ۵ پیام تستی
            try:
                await app.send_message(target_bot, message_text)
                count += 1
                await message.reply(f"📤 پیام #{count} ارسال شد")
                await asyncio.sleep(2)
            except Exception as e:
                await message.reply(f"❌ خطا: {e}")
                break

        sending = False
        await message.reply("🏁 تست کامل شد!")

    elif text == "توقف":
        sending = False
        await message.reply("⏹️ متوقف شد")

    else:
        await message.reply("❓ دستور نامعتبر. از 'شروع' استفاده کن")

app.run()
