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

akan = []
semua = []
for pair, d in data.items():
    if not pair.endswith('idr'): continue
    if "_" in pair: continue
    if pair in ['usdtidr','usdcidr']: continue
    try:
        high=float(d['high']); low=float(d['low']); last=float(d['last']); vol=float(d['vol_idr'])
        if low==0: continue
        # DEBUG 3 koin pertama
        if len(semua)<3:
            print(f"DEBUG {pair}: low={low} last={last} high={high} vol={vol}")

        total_pump = ((high-low)/low)*100
        naik_low = ((last-low)/low)*100 if low!=0 else 0
        
        # Simpan semua buat fallback
        if vol>=500000:
            semua.append({"coin": pair.replace('idr','').upper(), "total": total_pump, "naik": naik_low, "vol": vol})

        # Filter AKAN PUMP asli
        if vol>=1000000 and 0.5 <= naik_low <= 30:
            akan.append({"coin": pair.replace('idr','').upper(), "naik": naik_low, "vol": vol, "total": total_pump})
    except: continue

akan.sort(key=lambda x: x['vol'], reverse=True)
semua.sort(key=lambda x: x['total'], reverse=True)

print(f"Hasil scan: AKAN={len(akan)} SEMUA={len(semua)}")

# ANTI 0: Kalau akan pump <5, pakai semua (high vs low)
final = akan if len(akan)>=5 else semua
mode = "AKAN PUMP" if len(akan)>=5 else "ALL PUMP (market flat)"

top = final[:20]
msg = f"⏳ {mode} {now.strftime('%H:%M')} WIB\nScan 476 | {len(final)} koin | TOP 20:\n\n"
for s in top:
    if mode=="AKAN PUMP":
        msg+=f"👀 {s['coin']} +{s['naik']:.1f}% Vol {int(s['vol']/1000000)}jt (total +{s['total']:.1f}%)\n"
    else:
        msg+=f"🚀 {s['coin']} +{s['total']:.1f}% Vol {int(s['vol']/1000000)}jt\n"

msg+=f"\nTotal {len(final)} koin"
kirim_tele(msg)
print(f"Telegram terkirim! Mode {mode} Total {len(final)}")
