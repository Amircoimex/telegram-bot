import requests
import time
import re
import os

# دریافت API Key از متغیر محیطی
API_KEY = os.environ.get("GRIZZLYSMS_API_KEY")

def get_tunisian_number_for_telegram():
    if not API_KEY:
        print("❌ API Key تنظیم نشده است!")
        return None, None
        
    max_retries = 3
    for attempt in range(max_retries):
        print(f"📞 درحال دریافت شماره (تلاش {attempt + 1}/{max_retries})...")
        
        url = "https://grizzlysms.com/api/v1/order"
        params = {
            "key": API_KEY,
            "service": "telegram",
            "country": "tn"
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if data.get("status") == "success":
                phone_number = data["data"]["number"]
                order_id = data["data"]["order_id"]
                
                if re.match(r'^\+216[29]', phone_number):
                    print(f"✅ شماره مطلوب دریافت شد: {phone_number}")
                    return order_id, phone_number
                else:
                    print(f"⚠️ شماره نامطلوب: {phone_number} - لغو و درخواست مجدد...")
                    cancel_order(order_id)
                    continue
            else:
                print(f"❌ خطا: {data.get('message', 'Unknown error')}")
                continue
                
        except Exception as e:
            print(f"❌ خطای ارتباطی: {e}")
            continue
    
    print("❌ پس از چندین تلاش، شماره مطلوب یافت نشد")
    return None, None

def cancel_order(order_id):
    try:
        cancel_url = "https://grizzlysms.com/api/v1/cancel"
        params = {"key": API_KEY, "order_id": order_id}
        requests.get(cancel_url, params=params, timeout=10)
    except:
        pass

def get_sms_code(order_id):
    url = "https://grizzlysms.com/api/v1/sms"
    params = {"key": API_KEY, "order_id": order_id}
    
    print("⏳ در حال انتظار برای دریافت کد SMS...")
    
    for i in range(20):  # کاهش زمان انتظار
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get("status") == "success" and data["data"].get("sms"):
                sms_code = data["data"]["sms"]
                code_match = re.search(r'\b\d{4,6}\b', sms_code)
                if code_match:
                    return f"✅ کد تأیید: {code_match.group()}"
                return f"✅ کد تأیید: {sms_code}"
            
            print(f"🔁 چک کردن کد... ({i+1}/20)")
            time.sleep(10)
            
        except Exception as e:
            print(f"⚠️ خطا در چک کردن کد: {e}")
            time.sleep(10)
    
    return "❌ کد تأیید دریافت نشد"

def check_balance():
    try:
        balance_url = "https://grizzlysms.com/api/v1/balance"
        params = {"key": API_KEY}
        response = requests.get(balance_url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "success":
            balance = data["data"].get("balance", 0)
            currency = data["data"].get("currency", "USD")
            return f"💰 موجودی حساب: {balance} {currency}"
        else:
            return "❌ خطا در بررسی موجودی"
    except Exception as e:
        return f"❌ خطا در بررسی موجودی: {e}"

def main():
    print("🎯 سرویس دریافت شماره تونس برای تلگرام")
    print("=" * 40)
    
    # بررسی موجودی
    balance_info = check_balance()
    print(balance_info)
    
    # دریافت شماره
    order_id, phone_number = get_tunisian_number_for_telegram()
    
    if order_id and phone_number:
        print(f"\n📱 شماره: {phone_number}")
        print("⏳ در حال دریافت کد...")
        
        # دریافت کد تأیید
        sms_result = get_sms_code(order_id)
        print(sms_result)
    else:
        print("❌ دریافت شماره با مشکل مواجه شد")

if __name__ == "__main__":
    main()