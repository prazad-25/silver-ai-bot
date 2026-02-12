import requests

# BOT_TOKEN = "8537563016:AAF2XJEiSkusFYwWIhdUjWwpcsMlFOnfjFI"
# CHAT_ID = "1249041894"
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)
