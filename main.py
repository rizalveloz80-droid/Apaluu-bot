import os, requests
TOKEN=os.getenv("TELEGRAM_TOKEN")
CHAT=os.getenv("CHAT_ID")
requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT, "text": "✅ ALHAMDULILLAH NYALA - Kalau ini masuk berarti udah beres min!"})
