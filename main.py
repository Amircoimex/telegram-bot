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

print("🔍 تست دریافت پیام‌ها...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

# هندلر برای تمام پیام‌ها
@app.on_message()
async def handle_all_messages(client, message):
    print(f"📨 پیام جدید دریافت شد:")
    print(f"   از: {message.chat.username or message.chat.first_name}")
    print(f"   متن: '{message.text}'")
    print(f"   چت آیدی: {message.chat.id}")
    print("---")

@app.on_message(filters.chat("me") & filters.text)
async def handle_my_messages(client, message):
    if message.text == "شروع":
        await message.reply("✅ تست شروع شد!")
        # یک پیام تستی به بات هدف بفرست
        await app.send_message(target_bot, "🇹🇳 تونس JONS")
        await message.reply(f"📤 پیام تستی به @{target_bot} ارسال شد")

    elif message.text == "وضعیت":
        await message.reply("🤖 ربات در حال تست است")

print("🚀 ربات تستی آماده...")
app.run()
