import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WIB = timezone(timedelta(hours=7))

def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": pesan}, timeout=15)

now = datetime.now(WIB)
print(f"🔥 MODE AKAN PUMP 30-50 REAL START {now}")

data = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
print(f"Scan {len(data)} koin...")

signals = []
for pair, d in data.items():
    if not pair.endswith('idr'): continue
    if "_" in pair: continue
    if pair in ['usdtidr','usdcidr']: continue
    try:
        high = float(d['high']); low = float(d['low']); last = float(d['last']); vol = float(d['vol_idr'])
        if low == 0 or last == 0: continue
        if vol < 2000000: continue
        if last < 1: continue
        naik_low = ((last - low) / low) * 100
        if 1.0 <= naik_low <= 15.0 and high > last:
            signals.append({"coin": pair.replace('idr','').upper(), "naik": naik_low, "vol": vol})
    except: continue

signals.sort(key=lambda x: x['vol'], reverse=True)
print(f"Hasil scan: {len(signals)} AKAN PUMP - TARGET 30-50")

if not signals:
    kirim_tele(f"😴 Market kalem {now.strftime('%H:%M')} WIB - Scan 476 koin")
else:
    top = signals[:20]
    msg = f"⏳ AKAN PUMP {now.strftime('%H:%M')} WIB\nScan 476 | {len(signals)} koin 1-15% | TOP 20:\n\n"
    for s in top:
        msg += f"👀 {s['coin']} +{s['naik']:.1f}% Vol {int(s['vol']/1000000)}jt\n"
    kirim_tele(msg)
    print(f"Telegram terkirim! Top: {top[0]['coin']} +{top[0]['naik']:.1f}% - Total {len(signals)}")
