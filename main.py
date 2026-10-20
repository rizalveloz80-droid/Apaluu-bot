import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get('tickers', {})
    except: return {}

# BLACKLIST LENGKAP - YANG GA BISA SCALPING CEPAT JANGAN MASUK!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr',
    'btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','ada_idr','bnb_idr','trx_idr',
    'ern_idr','show_idr',
    # YANG LU MINTA BUANG:
    'hype_idr','pippin_idr','pepe_idr','sui_idr','fartcoin_idr','cake_idr','anoa_idr','ondo_idr','marscoin_idr'
}

tickers = get_tickers()
now = datetime.now().strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    try:
        last = float(d['last']); low = float(d['low']); high = float(d['high'])
        vol = float(d.get('vol_idr',0))
        if low==0: continue
        if last < low*0.9 or last > high*1.1: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 999
        result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v):
    return f"{v/1_000_000_000:.2f}Bn" if v>=1_000_000_000 else f"{v/1_000_000:.0f}jt"

# GOLD - VOL KECIL 300jt-1Bn (biar lincah, bukan 3Bn!)
gold = [x for x in result if 0 <= x['pct_low'] <= 5 and 300_000_000 <= x['vol'] <= 1_000_000_000]
gold = sorted(gold, key=lambda x: x['vol'], reverse=True)[:10]

# RUNNING - VOL KECIL 150jt-800jt (FAVORIT LU! SCALP CEPAT MODAL 100RB!)
running = [x for x in result if 10 <= x['pct_low'] <= 25 and 150_000_000 <= x['vol'] <= 800_000_000 and x['pct_high'] > 3]
running = sorted(running, key=lambda x: x['vol'], reverse=True)[:10]

super_big = [x for x in result if x['vol'] >= 2_000_000_000 and 0 <= x['pct_low'] <= 5]
super_big = sorted(super_big, key=lambda x: x['vol'], reverse=True)[:3]

pucuk = [x for x in result if x['pct_low'] > 25 and x['vol'] >= 150_000_000]
pucuk = sorted(pucuk, key=lambda x: x['pct_low'], reverse=True)[:5]

msg = f"V40 VOL KECIL {now} | {len(tickers)}->{len(result)} coin bersih!\n\n"
if super_big:
    msg += "🚨 SUPER ALT >2Bn (0-5% low):\n"
    for c in super_big: msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"
    msg += "\n"
if gold:
    msg += "⭐ GOLD BOTTOM 0-5% (300jt-1Bn):\n"
    for c in gold: msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"
    msg += "\n"
if running:
    msg += "🚀 RUNNING 10-25% VOL KECIL (150-800jt) SCALP CEPAT:\n"
    for c in running: msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low Vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"
else:
    msg += "🚀 RUNNING VOL KECIL: KOSONG\n\n"
if pucuk:
    msg += "⚠️ PUCUK >25% JANGAN ENTRY:\n"
    for c in pucuk: msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])}\n"

print(msg)
send_tele(msg)
