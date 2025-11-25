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

min_delay = 2
max_delay = 3
min_batch_size = 3
max_batch_size = 5
pause_time = 4

if not session_string:
    print("❌ SESSION_STRING پیدا نشد! لطفاً متغیر محیطی رو تنظیم کنید.")
    exit(1)

print("🚀 شروع ربات با Session String...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

sending = False

@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await app.send_message("me", "قبلاً شروع شده ✅")
            return

        sending = True
        await app.send_message("me", f"شروع شد ✅ هر پیام با فاصله {min_delay}-{max_delay} ثانیه و هر دسته {min_batch_size}-{max_batch_size} پیام ارسال می‌شود.")

        while sending:
            try:
                batch_size = random.randint(min_batch_size, max_batch_size)
                print(f"📦 ارسال دسته جدید با {batch_size} پیام")
                
                for i in range(batch_size):
                    if not sending:
                        break
                    
                    await app.send_message(target_bot, message_text)
                    print(f"پیام {i+1}/{batch_size} به @{target_bot} ارسال شد")
                    
                    if i < batch_size - 1:
                        delay = random.uniform(min_delay, max_delay)
                        print(f"⏸️ توقف {delay:.1f} ثانیه...")
                        await asyncio.sleep(delay)

                if sending:
                    print(f"⏸️ توقف {pause_time} ثانیه بین دسته‌ها...")
                    await asyncio.sleep(pause_time)

            except FloodWait as e:
                print(f"FloodWait: sleep {e.value}s")
                await asyncio.sleep(e.value)
            except RPCError as e:
                print("RPCError:", e)
                sending = False
                await asyncio.sleep(3)
            except Exception as e:
                print("Error:", e)
                sending = False
                await asyncio.sleep(3)

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            await app.send_message("me", "⛔ ارسال متوقف شد.")
        else:
            await app.send_message("me", "هیچ کاری در حال انجام نیست.")

    else:
        await app.send_message("me", "دستور نامعتبر است. از 'شروع' یا 'ایست' استفاده کن.")

print("🤖 ربات آماده کار است...")
app.run()
