import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print("TELE_TOKEN/CHAT_ID kosong!")
        return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"Telegram status: {r.status_code}")
        print(r.text[:500])
    except Exception as e:
        print(f"Telegram error: {e}")

def get_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get('tickers', {})
    except Exception as e:
        print(f"Error tickers: {e}")
        return {}

tickers = get_tickers()
print(f"Total ticker: {len(tickers)}")
now = datetime.now().strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'):
        continue
    try:
        last = float(d['last'])
        low = float(d['low'])
        high = float(d['high'])
        vol_idr = float(d.get('vol_idr', 0))
        if low == 0 or last == 0:
            continue
        # Fix ERN ghost: last harus di dalam range low-high
        if last < low*0.9 or last > high*1.1:
            continue
        pct_low = (last - low) / low * 100
        pct_high_dist = (high - last) / last * 100 if last>0 else 999
        result.append({
            'pair': pair,
            'last': last,
            'low': low,
            'high': high,
            'vol': vol_idr,
            'pct_low': pct_low,
            'pct_high_dist': pct_high_dist
        })
    except:
        continue

print(f"Filtered IDR: {len(result)}")

# GOLD 0-5%
gold = [x for x in result if 0 <= x['pct_low'] <= 5 and x['vol'] >= 300_000_000]
gold = sorted(gold, key=lambda x: x['vol'], reverse=True)[:10]

# RUNNING 10-25% - FAVORIT LU! SCALP CEPAT!
running = [x for x in result if 10 <= x['pct_low'] <= 25 and x['vol'] >= 400_000_000 and x['pct_high_dist'] > 3]
running = sorted(running, key=lambda x: x['pct_low'])[:10]

# SUPER PAUS >3Bn tapi masih 0-5% low
super_big = [x for x in result if x['vol'] >= 3_000_000_000 and 0 <= x['pct_low'] <= 5]
super_big = sorted(super_big, key=lambda x: x['vol'], reverse=True)[:5]

# PUCUK >25%
pucuk = [x for x in result if x['pct_low'] > 25 and x['vol'] >= 300_000_000]
pucuk = sorted(pucuk, key=lambda x: x['pct_low'], reverse=True)[:5]

def fmt_vol(v):
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.2f}Bn"
    else:
        return f"{v/1_000_000:.0f}jt"

msg = f"V38 RUNNING EDITION {now} | {len(tickers)}->{len(result)} coin\n\n"

if super_big:
    msg += "🚨 SUPER PAUS >3Bn (0-5% low):\n"
    for c in super_big:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"
    msg += "\n"

if gold:
    msg += "⭐ GOLD BOTTOM 0-5% low:\n"
    for c in gold:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"
    msg += "\n"

if running:
    msg += "🚀 RUNNING 10-25% (FAVORIT LU! SCALP CEPAT):\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low Vol {fmt_vol(c['vol'])} sisa ke high {c['pct_high_dist']:.0f}%\n"
    msg += "\n"
else:
    msg += "🚀 RUNNING 10-25%: KOSONG (market lagi diem)\n\n"

if pucuk:
    msg += "⚠️ PUCUK >25% JANGAN ENTRY:\n"
    for c in pucuk:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"

print(msg)
send_tele(msg)
