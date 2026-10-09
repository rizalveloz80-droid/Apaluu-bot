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

r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
tickers = r.get('tickers', r) # support 2 format
print(f"Scan {len(tickers)} koin...")

akan=[]
semua=[]
for pair, d in tickers.items():
    try:
        # support btc_idr dan btcidr
        if not pair.lower().endswith('idr'): continue
        coin = pair.replace('_idr','').replace('idr','').upper()
        if coin in ['USDT','USDC']: continue

        high=float(d['high']); low=float(d['low']); last=float(d['last']); vol=float(d.get('vol_idr', d.get('vol',0)))
        if low==0: continue

        total = ((high-low)/low)*100
        naik = ((last-low)/low)*100

        # DEBUG 3 koin
        if len(semua)<3:
            print(f"DEBUG {pair} {coin}: low={low} last={last} high={high} vol={vol} naik={naik:.2f}% total={total:.2f}%")

        if vol>=500000: # 500rb aja
            semua.append({"coin":coin, "total":total, "naik":naik, "vol":vol})
        if vol>=1000000 and 0.3 <= naik <= 25:
            akan.append({"coin":coin, "naik":naik, "vol":vol, "total":total})
    except Exception as e:
        if len(semua)<3:
            print(f"ERR {pair}: {e}")
        continue

akan.sort(key=lambda x: x['vol'], reverse=True)
semua.sort(key=lambda x: x['total'], reverse=True)

print(f"Hasil scan: AKAN={len(akan)} SEMUA={len(semua)}")

final = akan if len(akan)>=10 else semua
mode = "AKAN PUMP" if len(akan)>=10 else "ALL PUMP"

top = final[:20]
msg = f"⏳ {mode} {now.strftime('%H:%M')} WIB\nScan {len(tickers)} | {len(final)} koin | TOP 20:\n\n"
for s in top:
    msg+=f"👀 {s['coin']} +{s['naik']:.1f}% (H-L +{s['total']:.1f}%) Vol {int(s['vol']/1000000)}jt\n"

kirim_tele(msg)
print(f"Telegram terkirim! Mode {mode} Total {len(final)} Top {top[0]['coin'] if top else 'none'}")
