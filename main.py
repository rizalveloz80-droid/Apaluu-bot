import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    # TANPA Markdown biar KRD_ ga error
    requests.post(url, json={"chat_id": CHAT_ID, "text": pesan}, timeout=15)

print(f"🔥 MODE ALL COIN AGRESIF START {datetime.now()}")

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
print(f"Scan {len(tickers)} koin...")

signals = []
for coin, d in tickers.items():
    if not coin.endswith('idr'): continue
    if "_" in coin: continue # Skip koin aneh KRD_

    try:
        low = float(d['low'])
        last = float(d['last'])
        vol = float(d['vol_idr'])
        if low == 0: continue
        if vol < 10000000: continue # Minimal 10jt biar ga fake
        if last < 10: continue # Skip koin <10 rupiah yang gampang +600%

        # Pake LAST vs LOW, bukan HIGH vs LOW biar real
        pc = ((last - low) / low) * 100

        if pc >= 3.5:
            signals.append({"coin": coin.replace('idr','').upper(), "pc": round(pc,2), "vol": vol, "price": last})
    except:
        continue

signals.sort(key=lambda x: x['pc'], reverse=True)
print(f"Hasil scan: {len(signals)} lolos filter")

if not signals:
    kirim_tele(f"Market kalem jam {datetime.now().strftime('%H:%M')} - ga ada >3.5%")
else:
    top = signals[:20]
    pesan = f"💥 ALL COIN AGRESIF {datetime.now().strftime('%H:%M')} WIB\n"
    pesan += f"Scan 476 | {len(signals)} koin >3.5% (real) | TOP 20:\n\n"
    for s in top:
        pesan += f"🚀 {s['coin']} +{s['pc']}% | Vol {int(s['vol']/1000000)}jt\n"
    kirim_tele(pesan)
    print(f"Telegram terkirim! Top: {top[0]['coin']} +{top[0]['pc']}%")
