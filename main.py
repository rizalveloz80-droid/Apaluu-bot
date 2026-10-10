import os, requests
print("TES MULAI")
t = (os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
c = (os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()
print(f"TOKEN ADA:{bool(t)} CHAT ADA:{bool(c)}")
r = requests.post(f"https://api.telegram.org/bot{t}/sendMessage", data={"chat_id": c, "text": "✅ TEST JALAN 21:22 - kalo ini masuk, berarti GitHub ke Telegram udah nyambung!"}, timeout=20)
print(r.text)
