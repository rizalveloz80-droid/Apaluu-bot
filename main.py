import requests, os
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
print(f"TOKEN ada: {bool(TOKEN)} CHAT ada: {bool(CHAT)}")
r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT, "text": "🤖 TEST V12.1 - Kalo ini masuk berarti token aman min!"}, timeout=15)
print(f"Status: {r.status_code} - {r.text[:200]}")
