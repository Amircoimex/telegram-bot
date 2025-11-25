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

# تنظیمات پیشرفته
concurrent_searches = 5
search_timeout = 10
cooldown_duration = 60
request_delay = 2

if not session_string:
    print("❌ SESSION_STRING پیدا نشد!")
    exit(1)

print("🧠 ربات هوشمند راه‌اندازی شد...")
app = Client("my_session", api_id=api_id, api_hash=api_hash, session_string=session_string)

# متغیرهای حالت
sending = False
message_count = 0
active_searches = 0
cooldown_until = 0
successful_searches = 0
failed_searches = 0
start_time = 0
adaptive_delay = request_delay
adaptive_mode = True  # حالت تطبیقی

# هندلر برای پیام‌های بات هدف
@app.on_message(filters.user(target_bot))
async def check_search_status(client, message):
    global active_searches, cooldown_until, successful_searches, failed_searches, adaptive_delay
    
    if not sending:
        return
        
    if message.text:
        print(f"🎯 [{time.strftime('%H:%M:%S')}] از بات: '{message.text}'")
        
        # تشخیص خطای محدودیت
        if "نمی‌توانید بیش از 5 درخواست همزمان" in message.text:
            print("⏰ محدودیت تشخیص داده شد - توقف ۶۰ ثانیه")
            cooldown_until = time.time() + cooldown_duration
            if adaptive_mode:
                adaptive_delay = min(adaptive_delay + 0.5, 5)  # افزایش تاخیر تطبیقی
            return
        
        # تشخیص موفقیت‌آمیز بودن جستجو
        if "جستجوی شماره" not in message.text:
            if active_searches > 0:
                active_searches -= 1
            
            if "موجود نیست" in message.text:
                failed_searches += 1
                print("❌ جستجو ناموفق")
            else:
                successful_searches += 1
                print("✅ جستجو موفق")
                
            # کاهش تاخیر تطبیقی در صورت موفقیت
            if adaptive_mode and successful_searches % 3 == 0:
                adaptive_delay = max(adaptive_delay - 0.2, 1)
            
            print(f"📊 جستجوهای فعال: {active_searches}")

async def auto_complete_search():
    """اتمام خودکار جستجو"""
    await asyncio.sleep(search_timeout)
    
    global active_searches, failed_searches
    if active_searches > 0:
        active_searches -= 1
        failed_searches += 1
        print(f"⏰ جستجو خودکار تمام شد")

def calculate_stats():
    """محاسبه آمار عملکرد"""
    if message_count == 0:
        return "آمار موجود نیست"
    
    elapsed = time.time() - start_time
    speed = message_count / (elapsed / 60) if elapsed > 0 else 0  # پیام در دقیقه
    success_rate = (successful_searches / message_count) * 100 if message_count > 0 else 0
    
    return f"""
📊 آمار عملکرد:
├─ سرعت: {speed:.1f} پیام/دقیقه
├─ موفق: {successful_searches} جستجو
├─ ناموفق: {failed_searches} جستجو  
└─ موفقیت: {success_rate:.1f}%
"""

# هندلر اصلی
@app.on_message(filters.chat("me") & filters.text)
async def handler(client, message):
    global sending, message_count, active_searches, cooldown_until
    global successful_searches, failed_searches, start_time, adaptive_delay, adaptive_mode
    
    text = message.text.strip()

    if text == "شروع":
        if sending:
            await app.send_message("me", "⏳ قبلاً شروع شده!")
            return

        sending = True
        message_count = 0
        active_searches = 0
        cooldown_until = 0
        successful_searches = 0
        failed_searches = 0
        start_time = time.time()
        adaptive_delay = request_delay
        
        status_msg = await app.send_message("me", 
            f"🚀 ربات هوشمند شروع به کار کرد!\n"
            f"🔧 حالت تطبیقی: {'فعال' if adaptive_mode else 'غیرفعال'}\n"
            f"⏰ تاخیر فعلی: {adaptive_delay} ثانیه"
        )

        while sending:
            try:
                # بررسی کول‌داون
                current_time = time.time()
                if current_time < cooldown_until:
                    remaining = int(cooldown_until - current_time)
                    if remaining % 10 == 0:  # فقط هر ۱۰ ثانیه لاگ کن
                        print(f"⏳ کول‌داون: {remaining} ثانیه")
                    await asyncio.sleep(5)
                    continue
                
                # ارسال درخواست‌های جدید
                while active_searches < concurrent_searches and sending:
                    await app.send_message(target_bot, message_text)
                    message_count += 1
                    active_searches += 1
                    
                    print(f"📤 [{time.strftime('%H:%M:%S')}] پیام #{message_count} - فعال: {active_searches}/{concurrent_searches}")
                    
                    # تایمر جستجو
                    asyncio.create_task(auto_complete_search())
                    
                    # تاخیر تطبیقی بین درخواست‌ها
                    if active_searches < concurrent_searches:
                        await asyncio.sleep(adaptive_delay)
                
                # به روزرسانی وضعیت هر ۳۰ ثانیه
                if int(time.time() - start_time) % 30 == 0:
                    stats = calculate_stats()
                    await status_msg.edit(
                        f"🟢 در حال اجرا...\n"
                        f"📤 ارسال شده: {message_count}\n"
                        f"🔍 فعال: {active_searches}/{concurrent_searches}\n"
                        f"⏰ تاخیر: {adaptive_delay:.1f} ثانیه\n"
                        f"{stats}"
                    )
                
                await asyncio.sleep(2)

            except FloodWait as e:
                print(f"⏳ FloodWait: {e.value} ثانیه")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"❌ خطا: {e}")
                await asyncio.sleep(3)

    elif text == "وضعیت":
        stats = calculate_stats()
        status = "🟢 در حال اجرا" if sending else "🔴 متوقف"
        
        await app.send_message("me",
            f"{status}\n"
            f"📤 پیام‌ها: {message_count}\n"
            f"🔍 جستجوهای فعال: {active_searches}/{concurrent_searches}\n"
            f"✅ موفق: {successful_searches}\n"
            f"❌ ناموفق: {failed_searches}\n"
            f"⏰ تاخیر: {adaptive_delay:.1f} ثانیه\n"
            f"{stats}"
        )

    elif text == "آمار":
        stats = calculate_stats()
        await app.send_message("me", stats)

    elif text == "تطبیق":
        adaptive_mode = not adaptive_mode
        status = "فعال" if adaptive_mode else "غیرفعال"
        await app.send_message("me", f"🔧 حالت تطبیقی {status} شد")

    elif text in ["ایست", "توقف"]:
        if sending:
            sending = False
            stats = calculate_stats()
            await app.send_message("me",
                f"⛔ ربات متوقف شد\n"
                f"📊 عملکرد کلی:\n"
                f"├─ کل پیام‌ها: {message_count}\n"
                f"├─ موفق: {successful_searches}\n"
                f"├─ ناموفق: {failed_searches}\n"
                f"└─ زمان اجرا: {int((time.time() - start_time) / 60)} دقیقه\n"
                f"{stats}"
            )
        else:
            await app.send_message("me", "🔴 ربات از قبل متوقف است")

    else:
        await app.send_message("me", 
            "🤖 دستورات ربات:\n"
            "├─ شروع - اجرای ربات\n"
            "├─ توقف - توقف ربات\n"
            "├─ وضعیت - نمایش وضعیت\n"
            "├─ آمار - آمار عملکرد\n"
            "└─ تطبیق - تغییر حالت تطبیقی"
        )

print("🤖 ربات هوشمند آماده کار است...")
app.run()
