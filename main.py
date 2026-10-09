import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": pesan}, timeout=15)

print(f"🔥 MODE ALL COIN AGRESIF START {datetime.now()}")

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
print(f"Scan {len(tickers)} koin...")

signals = []
for coin, d in tickers.items():
    if not coin.endswith('idr'): continue
    if "_" in coin: continue
    if coin in ['usdtidr','usdcidr']: continue

    try:
        high = float(d['high'])
        low = float(d['low'])
        last = float(d['last'])
        vol = float(d['vol_idr'])
        if low == 0: continue
        if vol < 2000000: continue # 2jt aja cukup buat micin
        if last == 0: continue

        # BALIK ke HIGH vs LOW biar agresif lagi, tapi max 100% biar ga +600% fake
        pc = ((high - low) / low) * 100

        if 3.5 <= pc <= 100: # 3.5% - 100% itu pump real
            signals.append({"coin": coin.replace('idr','').upper(), "pc": round(pc,2), "vol": vol, "price": last})
    except:
        continue

signals.sort(key=lambda x: x['pc'], reverse=True)
print(f"Hasil scan: {len(signals)} lolos filter")

if not signals:
    kirim_tele(f"Market kalem {datetime.now().strftime('%H:%M')} WIB - Scan 476 koin, 0 pump >3.5%")
    print("Kalem")
else:
    top = signals[:20]
    pesan = f"💥 ALL COIN AGRESIF {datetime.now().strftime('%H:%M')} WIB\n"
    pesan += f"Scan 476 | {len(signals)} koin pump | TOP 20:\n\n"
    for s in top:
        pesan += f"🚀 {s['coin']} +{s['pc']}% Vol {int(s['vol']/1000000)}jt\n"

    kirim_tele(pesan)
    print(f"Telegram terkirim! Top: {top[0]['coin']} +{top[0]['pc']}%")
