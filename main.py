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

min_delay = 1  # حداقل فاصله ۱ ثانیه
max_delay = 3  # حداکثر فاصله ۳ ثانیه

if not session_string:
    print("❌ SESSION_STRING پیدا نشد! لطفاً متغیر محیطی رو تنظیم کنید.")
    exit(1)

print("🚀 شروع ربات با Session String...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False
message_count = 0

@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending, message_count
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await app.send_message("me", "قبلاً شروع شده ✅")
            return

        sending = True
        message_count = 0
        await app.send_message("me", f"شروع شد ✅ هر پیام با فاصله {min_delay}-{max_delay} ثانیه ارسال می‌شود.")

        while sending:
            try:
                # ارسال پیام
                await app.send_message(target_bot, message_text)
                message_count += 1
                print(f"📤 پیام #{message_count} به @{target_bot} ارسال شد")
                
                # فاصله تصادفی بین پیام‌ها
                delay = random.uniform(min_delay, max_delay)
                print(f"⏸️ توقف {delay:.1f} ثانیه...")
                await asyncio.sleep(delay)

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
        await app.send_message("me", f"وضعیت ربات: {status}\nتعداد پیام‌های ارسالی: {message_count}")

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            await app.send_message("me", f"⛔ ارسال متوقف شد.\nتعداد کل پیام‌های ارسالی: {message_count}")
        else:
            await app.send_message("me", "هیچ کاری در حال انجام نیست.")

    else:
        await app.send_message("me", "دستور نامعتبر است. از 'شروع' یا 'ایست' استفاده کن.")

print("🤖 ربات آماده کار است...")
app.run()
