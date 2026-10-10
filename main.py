import os, requests, pytz
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

print(f"TOKEN ADA: {bool(TOKEN)} | CHAT_ID: {CHAT_ID}")

if not TOKEN or not CHAT_ID:
    print("TOKEN/CHAT_ID KOSONG!")
    exit(0)

def kirim(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}
    r = requests.post(url, data=data, timeout=20)
    print(f"KIRIM: {r.status_code}")
    return r

# === SCAN TOP 7 BORONGAN ASLI ===
wib = datetime.now(pytz.timezone('Asia/Jakarta'))
jam = wib.strftime("%H:%M WIB")

try:
    # Ambil data Indodax
    tick = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers = tick.get("tickers", {})

    hasil = []
    for koin, data in tickers.items():
        if not koin.endswith("_idr"): continue
        try:
            last = float(data.get("last", 0))
            low = float(data.get("low", 0))
            high = float(data.get("high", 0))
            vol = float(data.get(f"vol_{koin.split('_')[0]}", 0))
            if low == 0: continue

            gain_hl = ((high - low) / low) * 100 # H-L %
            # Gain 24j (last vs low approximation)
            gain = ((last - low) / low) * 100

            if 0.5 <= gain <= 6.0 and 2.0 <= gain_hl <= 8.0 and vol > 0:
                hasil.append((koin.upper().replace("_IDR",""), gain, gain_hl, vol, last))
        except:
            continue

    # Sort by volume / gain
    hasil = sorted(hasil, key=lambda x: x[3], reverse=True)[:7]

    if not hasil:
        pesan = f"🤖 <b>Bot hidup {jam} - Scan 0, market sepi, next 5 menit lagi</b>\n\nFilter: Gain 0.5-6.0% H-L 2.0-8.0% | All\nCoin Hunter 24JAM\nFokus No 1-3 aja min!"
    else:
        txt = f"🔥 <b>TOP 7 BORONGAN APALUU - {jam}</b>\n\n"
        txt += f"Filter: Gain 0.5-6.0% H-L 2.0-8.0% | All\nCoin Hunter 24JAM\n\n"
        for i, (coin, g, ghl, v, last) in enumerate(hasil, 1):
            txt += f"{i}. {coin} | Gain {g:.2f}% | H-L {ghl:.2f}% | Vol {v:.0f}\n"
        txt += f"\nFokus No 1-3 aja min!\nWaktu: {wib.strftime('%d-%m %H:%M')} WIB"
        pesan = txt

except Exception as e:
    print(f"Error scan: {e}")
    pesan = f"🤖 <b>Bot hidup {jam} - Scan error: {e}, next 5 menit lagi</b>"

kirim(pesan)
