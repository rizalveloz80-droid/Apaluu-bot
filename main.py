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
        high = float(d['high'])
        low = float(d['low'])
        last = float(d['last'])
        vol = float(d['vol_idr'])
        if low == 0 or last == 0: continue
        if vol < 5000000: continue # 5jt minimal
        if last < 1: continue

        naik_low = ((last - low) / low) * 100
        # AKAN PUMP: baru naik 2% - 10% dari low hari ini
        # Belum ketinggian, masih awal!
        if 2.0 <= naik_low <= 10.0:
            # Pastikan high masih di atas last (masih ada ruang naik)
            if high > last:
                signals.append({"coin": pair.replace('idr','').upper(), "naik": naik_low, "vol": vol, "last": last})
    except:
        continue

signals.sort(key=lambda x: x['vol'], reverse=True) # Urut Vol terbesar = yang paling ramai = paling siap pump
print(f"Hasil scan: {len(signals)} AKAN PUMP - TARGET 30-50")

if not signals:
    kirim_tele(f"😴 Market kalem {now.strftime('%H:%M')} WIB - 476 koin belum ada yang mulai naik 2%")
else:
    top = signals[:20]
    msg = f"⏳ AKAN PUMP {now.strftime('%H:%M')} WIB\n"
    msg += f"Scan 476 | {len(signals)} koin baru naik 2-10% | TOP 20 VOL GEDE:\n\n"
    for s in top:
        msg += f"👀 {s['coin']} +{s['naik']:.1f}% Vol {int(s['vol']/1000000)}jt\n"
    msg += f"\nEntry sekarang sebelum terbang! Total {len(signals)} koin fase awal"
    kirim_tele(msg)
    print(f"Telegram terkirim! Top AKAN PUMP: {top[0]['coin']} +{top[0]['naik']:.1f}%")
