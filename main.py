import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WIB = timezone(timedelta(hours=7))

def kirim_tele(pesan):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": pesan}, timeout=15)
        print(f"TELEGRAM STATUS: {r.status_code} {r.text[:200]}")
        return r
    except Exception as e:
        print(f"TELEGRAM ERROR: {e}")

now = datetime.now(WIB)
print(f"🔥 MODE AKAN PUMP 30-50 REAL START {now}")

data = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
print(f"Scan {len(data)} koin...")

signals=[]
for pair,d in data.items():
    if not pair.lower().endswith('idr'): continue
    coin=pair.replace('_idr','').replace('idr','').upper()
    if coin in ['USDT','USDC','BTC','ETH']: continue
    try:
        high=float(d['high']); low=float(d['low']); last=float(d['last']); vol=float(d.get('vol_idr',0))
        if low==0 or vol<10000000: continue
        if last<10: continue
        naik=((last-low)/low)*100
        total=((high-low)/low)*100
        if 3.0 <= naik <= 12.0 and 4.0 <= total <= 50.0:
            signals.append({"coin":coin, "naik":naik, "total":total, "vol":vol})
    except: continue

signals.sort(key=lambda x: x['naik'], reverse=True)
print(f"Hasil scan: {len(signals)} AKAN PUMP - TARGET 30-50")

if not signals:
    kirim_tele(f"😴 Market kalem {now.strftime('%H:%M')} WIB - {len(data)} koin ga ada yang 3-12%")
else:
    top=signals[:20]
    msg=f"⏳ AKAN PUMP {now.strftime('%H:%M')} WIB\n"
    msg+=f"Scan {len(data)} | {len(signals)} koin REAL 30-50 | TOP 20:\n\n"
    for s in top:
        msg+=f"👀 {s['coin']} +{s['naik']:.1f}% (H-L {s['total']:.1f}%) Vol {int(s['vol']/1000000)}jt\n"
    msg+=f"\nTotal {len(signals)} koin fase awal"
    kirim_tele(msg)
    print(f"Top: {top[0]['coin']} Total {len(signals)}")
