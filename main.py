import asyncio
import os
from pyrogram import Client, filters

api_id = int(os.environ.get("API_ID", 38528329))
api_hash = os.environ.get("API_HASH", "61564de233d29aff8737fce91232a4e8")
session_string = os.environ.get("SESSION_STRING", "")
target_bot = os.environ.get("TARGET_BOT", "ten_number_bot")

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🔍 تست دریافت پیام از بات هدف...")
print(f"🎯 بات هدف: @{target_bot}")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

# هندلر برای تمام پیام‌ها
@app.on_message()
async def handle_all_messages(client, message):
    # فقط پیام‌های مربوط به بات هدف رو نمایش بده
    if message.chat.username == target_bot.replace("@", ""):
        print(f"🎯 پیام از بات هدف:")
        print(f"   متن: '{message.text}'")
        print(f"   چت آیدی: {message.chat.id}")
        print(f"   یوزرنیم: @{message.chat.username}")
        print("---")
    elif message.chat.id == 7626529274:  # چت شما
        print(f"👤 پیام از شما: '{message.text}'")

@app.on_message(filters.chat("me") & filters.text)
async def handle_my_messages(client, message):
    if message.text == "شروع":
        await message.reply("✅ تست شروع شد!")
        
        # تست ارسال به بات هدف
        try:
            sent_message = await app.send_message(target_bot, "🇹🇳 تونس JONS")
            await message.reply(f"📤 پیام به @{target_bot} ارسال شد")
            print(f"✅ پیام به @{target_bot} ارسال شد")
        except Exception as e:
            await message.reply(f"❌ خطا در ارسال: {e}")
            print(f"❌ خطا در ارسال: {e}")

    elif message.text == "وضعیت":
        await message.reply("🤖 در حال تست بات هدف")

print("🚀 ربات تستی آماده...")
app.run()
