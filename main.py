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
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get('tickers', {})
    except:
        return {}

# === BLACKLIST YANG GA BISA SCALPING CEPAT ===
BLACKLIST = {
    # Stablecoin - harga patok, ga gerak!
    'usdt_idr', 'usdc_idr', 'dai_idr', 'busd_idr', 'paxg_idr', 't_idr',
    # Paus berat - modal 100rb ga kerasa!
    'btc_idr', 'eth_idr', 'xrp_idr', 'sol_idr', 'doge_idr', 'ada_idr', 'bnb_idr', 'trx_idr',
    # Hantu ERN & SHOW - vol tipu2!
    'ern_idr', 'show_idr'
}

tickers = get_tickers()
now = datetime.now().strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'):
        continue
    if pair in BLACKLIST:  # <--- LANGSUNG SKIP YANG DI BLACKLIST!
        continue
    try:
        last = float(d['last'])
        low = float(d['low'])
        high = float(d['high'])
        vol_idr = float(d.get('vol_idr', 0))
        if low == 0 or last == 0:
            continue
        if last < low*0.9 or last > high*1.1: # ghost filter
            continue
        pct_low = (last - low) / low * 100
        pct_high_dist = (high - last) / last * 100 if last>0 else 999
        result.append({
            'pair': pair, 'last': last, 'low': low, 'high': high,
            'vol': vol_idr, 'pct_low': pct_low, 'pct_high_dist': pct_high_dist
        })
    except:
        continue

def fmt_vol(v):
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.2f}Bn"
    return f"{v/1_000_000:.0f}jt"

# Filter bersih tanpa stable & paus berat!
gold = [x for x in result if 0 <= x['pct_low'] <= 5 and x['vol'] >= 300_000_000]
gold = sorted(gold, key=lambda x: x['vol'], reverse=True)[:10]

running = [x for x in result if 10 <= x['pct_low'] <= 25 and x['vol'] >= 400_000_000 and x['pct_high_dist'] > 3]
running = sorted(running, key=lambda x: x['vol'], reverse=True)[:10]

super_big = [x for x in result if x['vol'] >= 3_000_000_000 and 0 <= x['pct_low'] <= 5]
super_big = sorted(super_big, key=lambda x: x['vol'], reverse=True)[:5]

pucuk = [x for x in result if x['pct_low'] > 25 and x['vol'] >= 300_000_000]
pucuk = sorted(pucuk, key=lambda x: x['pct_low'], reverse=True)[:5]

msg = f"V39 ANTI-STABLE {now} | {len(tickers)}->{len(result)} coin (bersih!)\n\n"

if super_big:
    msg += "🚨 SUPER PAUS ALT >3Bn (0-5% low):\n"
    for c in super_big:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"
    msg += "\n"

if gold:
    msg += "⭐ GOLD BOTTOM 0-5% low:\n"
    for c in gold:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"
    msg += "\n"

if running:
    msg += "🚀 RUNNING 10-25% (SCALP CEPAT!):\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low Vol {fmt_vol(c['vol'])} sisa {c['pct_high_dist']:.0f}%\n"
    msg += "\n"
else:
    msg += "🚀 RUNNING 10-25%: KOSONG (market diem)\n\n"

if pucuk:
    msg += "⚠️ PUCUK >25% JANGAN ENTRY:\n"
    for c in pucuk:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"

print(msg)
send_tele(msg)
