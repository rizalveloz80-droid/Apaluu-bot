import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WIB = timezone(timedelta(hours=7))

def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": pesan}, timeout=15)

now = datetime.now(WIB)
print(f"🔥 MODE ALL COIN AGRESIF START {now}")

data = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
print(f"Scan {len(data)} koin...")

signals = []
for pair, d in data.items():
    if not pair.endswith('idr'): continue
    try:
        high = float(d['high'])
        low = float(d['low'])
        vol = float(d['vol_idr'])
        if low == 0: continue
        # GA ADA FILTER VOL! MICIN 100rb pun masuk!
        pc = ((high - low) / low) * 100
        if pc >= 2.0: # Turunin ke 2% aja biar jam sepi tetep dapet
            signals.append((pair.replace('idr','').upper(), pc, vol))
    except:
        continue

signals.sort(key=lambda x: x[1], reverse=True)
print(f"Hasil scan: {len(signals)} lolos filter")

if not signals:
    kirim_tele(f"Market super sepi {now.strftime('%H:%M')} WIB - 476 koin ga ada yang >2%")
else:
    top = signals[:25]
    msg = f"💥 ALL COIN AGRESIF {now.strftime('%H:%M')} WIB\nScan 476 | {len(signals)} pump >2% | TOP 25:\n\n"
    for coin, pc, vol in top:
        msg += f"{coin} +{pc:.2f}% Vol {int(vol/1000000)}jt\n"
    kirim_tele(msg)
    print(f"Telegram terkirim! Top {top[0][0]} +{top[0][1]:.2f}%")
