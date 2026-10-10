import os, requests, pytz
from datetime import datetime
import json

# AMBIL DARI SECRET LU
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

print(f"CEK TOKEN ADA? {bool(TOKEN)}")
print(f"CEK CHAT_ID ADA? {bool(CHAT_ID)} - Value: {CHAT_ID}")

if not TOKEN or not CHAT_ID:
    print("TOKEN/CHAT_ID KOSONG! CEK SECRETS DI GITHUB!")
    exit(0)

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}
    r = requests.post(url, data=data)
    print(f"KIRIM OK: {r.status_code} - {r.text[:200]}")
    return r

# CONTOH PESAN TEST - NANTI GANTI SAMA LOGIC TOP 7 LU
wib = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%H:%M")
pesan = f"✅ <b>APALUU BOT TEST {wib} WIB</b>\n\nBot jalan normal min! TOKEN & CHAT_ID udah konek.\n\nNext: scan TOP 7 BORONGAN jam {wib}"
kirim_telegram(pesan)
