import requests

BOT_TOKEN = "8537563016:AAHMjz-5hfEjUTVADjC5aTOBInw7az7TNh0"
CHAT_ID = "1249041894"


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
