import os
import logging
from flask import Flask, request
import requests

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8754473230:AAEF0yKKLMtLZLrd53k-xVy9PlackW15v_A")
MANAGER_ID = os.environ.get("MANAGER_ID", "8131102104")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

WELCOME_TEXT = """📚 *Привет! Это FlashBook — дизайнерские фотоальбомы* 🌿

Мы создаём красивые фотокниги на любую тему: путешествия, свадьба, любовь, семья и многое другое.

*💰 Наши цены:*

📖 *30 страниц* — 555 000 сум
_30–40 фотографий, формат A4_

📗 *40 страниц* — 655 000 сум ⭐️ Хит
_45–55 фотографий, формат A4_

📘 *60 страниц* — 855 000 сум
_65–75 фотографий, формат A4_

✅ Твёрдая матовая обложка
✅ Индивидуальный дизайн
✅ Готово за 5 рабочих дней

Выберите тариф и оформите заказ на сайте 👇"""

FALLBACK_TEXT = """Привет! 👋

По всем вопросам и деталям заказа свяжитесь с нашим менеджером — он ответит быстро 😊

👤 @flashbookuz"""

SITE_URL = "https://flashbookuz.netlify.app"

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{API}/sendMessage", json=payload)

def notify_manager(user):
    username = f"@{user['username']}" if user.get("username") else "нет username"
    first = user.get("first_name", "")
    last = user.get("last_name", "")
    name = f"{first} {last}".strip()
    user_id = user.get("id", "")
    text = (
        f"🔔 *Новый клиент написал боту!*\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Username: {username}\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"💬 Напишите ему: tg://user?id={user_id}"
    )
    send_message(MANAGER_ID, text)

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if not data or "message" not in data:
        return "ok"

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    user = msg.get("from", {})
    text = msg.get("text", "")

    if text.startswith("/start"):
        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "🌐 Заказать на сайте",
                    "url": SITE_URL
                }
            ], [
                {
                    "text": "💬 Написать менеджеру",
                    "url": "https://t.me/flashbookuz"
                }
            ]]
        }
        send_message(chat_id, WELCOME_TEXT, reply_markup=keyboard)
        notify_manager(user)

    elif text.startswith("/prices") or text.lower() in ["цены", "цена", "прайс", "стоимость", "сколько стоит", "сколько"]:
        keyboard = {
            "inline_keyboard": [[
                {"text": "🌐 Заказать на сайте", "url": SITE_URL}
            ]]
        }
        send_message(chat_id, WELCOME_TEXT, reply_markup=keyboard)

    else:
        keyboard = {
            "inline_keyboard": [[
                {"text": "👤 Написать менеджеру", "url": "https://t.me/flashbookuz"}
            ], [
                {"text": "🌐 Перейти на сайт", "url": SITE_URL}
            ]]
        }
        send_message(chat_id, FALLBACK_TEXT, reply_markup=keyboard)
        notify_manager(user)

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "FlashBook Bot is running! 🌿"

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    webhook_url = os.environ.get("WEBHOOK_URL", "")
    if not webhook_url:
        return "WEBHOOK_URL not set", 400
    url = f"{API}/setWebhook?url={webhook_url}/webhook/{BOT_TOKEN}"
    resp = requests.get(url)
    return resp.json()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
