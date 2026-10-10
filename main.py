import os, requests, pytz
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

print(f"TOKEN ADA: {bool(TOKEN)} | CHAT_ID: {CHAT_ID}")

if not TOKEN or not CHAT_ID:
    print("TOKEN/CHAT_ID KOSONG - CEK SECRETS!")
    exit(0)

def kirim(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}
    r = requests.post(url, data=data)
    print(f"KIRIM: {r.status_code} - {r.text[:400]}")
    return r

wib = datetime.now(pytz.timezone('Asia/Jakarta'))
jam = wib.strftime("%H:%M WIB")

# === LOGIC TOP 7 LU DISINI ===
# Contoh template biar ga kosong dulu
pesan = f"""🔥 <b>TOP 7 BORONGAN APALUU - {jam}</b>

✅ Bot Jalan! #107 Success 15s

1. ...
2. ...
3. ...
4. ...
5. ...
6. ...
7. ...

Auto scan tiap 5 menit, ga mati lagi di 14.58!

Waktu: {wib.strftime('%d-%m-%Y %H:%M:%S')}"""

kirim(pesan)
