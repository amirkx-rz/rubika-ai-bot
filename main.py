import os
import time
import threading
import requests
from flask import Flask

# ---------------- وب‌سرور سبک برای رندر ----------------
app_server = Flask(__name__)

@app_server.route('/')
def home():
    return "🤖 Rubika AI Bot is Running 24/7 on Render!"

# ---------------- تنظیمات ربات و هوش مصنوعی ----------------
RUBIKA_BOT_TOKEN = "توکن_ربات_روبیکا"
OPENROUTER_API_KEY = "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"
RUBIKA_API_URL = f"https://botapi.rubika.ir/v01/{CFAGAF0VFSUNMGMTDFHVRTDESNWAGFVEIRKVBBNKHHKWZALUKGWFSLJGPLMTLMGW}"

def ask_ai(user_text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://rubika.ir",
        "X-Title": "Rubika Bot"
    }
    system_prompt = (
        "تو یک عضو شوخ‌طبع، بسیار باحال، رفیق و صمیمی هستی. "
        "اصلاً رسمی حرف نزن. پاسخ‌هایت خیلی کوتاه، عامیانه، تند و به زبان روز فارسی باشد. "
        "هرگز مراحل تفکر یا انگلیسی ننویس و مستقیماً فقط جواب فارسی را بنویس."
    )
    payload = {
        "model": "nvidia/nemotron-3.5-lightning:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 100
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI Error: {e}")
    return "چاکرم، یه لحظه قاطی کردم دوباره بگو!"

def get_updates(offset=None):
    payload = {"limit": 10}
    if offset:
        payload["offset"] = offset
    try:
        res = requests.post(f"{RUBIKA_API_URL}/getUpdates", json=payload, timeout=25)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"Update Error: {e}")
    return None

def send_message(chat_id, text, reply_to_message_id=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    try:
        requests.post(f"{RUBIKA_API_URL}/sendMessage", json=payload, timeout=15)
    except Exception as e:
        print(f"Send Error: {e}")

# چرخه دریافت و ارسال پیام در پس‌زمینه
def bot_worker():
    print("ربات روبیکا در پس‌زمینه سرور رندر شروع به کار کرد...")
    last_update_id = None
    while True:
        try:
            data = get_updates(last_update_id)
            if data and data.get("status") == "OK":
                updates = data.get("data", {}).get("updates", [])
                for update in updates:
                    last_update_id = update.get("update_id")
                    if update.get("type") == "NewMessage":
                        msg = update.get("new_message", {})
                        chat_id = msg.get("chat_id")
                        text = msg.get("text", "")
                        msg_id = msg.get("message_id")
                        if text:
                            print(f"پیام دریافتی: {text}")
                            reply = ask_ai(text)
                            send_message(chat_id, reply, reply_to_message_id=msg_id)
        except Exception as err:
            print(f"Loop Error: {err}")
        time.sleep(2)

# اجرای ربات در ترد مستقل
threading.Thread(target=bot_worker, daemon=True).start()

if __name__ == "__main__":
    # اتصال به پورتی که رندر به طور خودکار تعیین می‌کند
    port = int(os.environ.get("PORT", 5000))
    app_server.run(host="0.0.0.0", port=port)
