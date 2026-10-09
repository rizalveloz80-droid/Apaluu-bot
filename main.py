import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    # Potong pesan kalo kepanjangan biar ga gagal kirim kaya tadi
    if len(pesan) > 4000:
        pesan = pesan[:4000] + "\n...kepotong 4000 huruf"
    requests.post(url, json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}, timeout=15)

print(f"🔥 MODE ALL COIN AGRESIF START {datetime.now()}")

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
print(f"Scan {len(tickers)} koin...")

signals = []
for coin, d in tickers.items():
    if not coin.endswith('idr'): continue
    # SEMUA MASUK! GA ADA YANG DI SKIP! Micin, btc, usdt masuk semua
    try:
        high = float(d['high'])
        low = float(d['low'])
        last = float(d['last'])
        vol = float(d['vol_idr'])
        if low == 0: continue

        pc = ((high - low) / low) * 100

        # AI MINTA: 3.5% - 50% SEMUA MASUK
        if pc >= 3.5:
            signals.append({"coin": coin.replace('idr','').upper(), "pc": round(pc,2), "vol": vol, "price": last})
    except:
        continue

signals.sort(key=lambda x: x['pc'], reverse=True)
print(f"Hasil scan: {len(signals)} lolos filter")

if not signals:
    pesan = f"Market kalem - Ga ada koin >3.5% jam {datetime.now().strftime('%H:%M')}"
    kirim_tele(pesan)
else:
    # Kirim TOP 20 aja biar ga kepanjangan kaya 227 tadi yang bikin gagal
    # Tapi di log tetep kehitung 227
    top = signals[:20]
    pesan = f"💥 *ALL COIN AGRESIF {datetime.now().strftime('%H:%M')} WIB*\n"
    pesan += f"Scan {len(tickers)} | {len(signals)} koin >3.5% | TOP 20 TERLIAR:\n\n"
    for s in top:
        pesan += f"🚀 *{s['coin']}* +{s['pc']}% | Rp{int(s['vol']/1000000)}jt\n"

    pesan += f"\nTotal {len(signals)} koin pump, cek log buat lengkapnya"
    kirim_tele(pesan)
    print(f"Telegram terkirim! Top: {top[0]['coin']} +{top[0]['pc']}%")
