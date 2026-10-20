import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_tickers():
    try:
        return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr'}

tickers = get_tickers()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    try:
        last = float(d['last']); low = float(d['low']); high = float(d['high'])
        vol = float(d.get('vol_idr', 0)); chg = float(d.get('change', 0))
        if low==0 or last<20: continue
        if vol<100_000_000 or vol>10_000_000_000: continue
        pct_low = (last-low)/low*100
        pct_high = (high-last)/last*100
        range_pct = (high-low)/low*100
        mid = (high+low)/2
        if range_pct>100 or pct_low<3: continue
        result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high,'chg':chg,'range_pct':range_pct,'mid':mid,'last':last})
    except: continue

def fmt_vol(v):
    return f"{v/1e9:.2f} Bn" if v>=1e9 else f"{v/1e6:.0f} Mn"

# ===== V53 FINAL LOCK - 5 KOIN PROPOR SIONAL - GA DIUBAH LAGI! =====

# 2 KOIN AKAN RUNNING - POND LOLOS, DRX KE-FILTER!
akan = sorted([
    x for x in result 
    if 3 <= x['pct_low'] <= 12
    and 8 <= x['range_pct'] <= 40  # POND 27% LOLOS, DRX 82% KE-FILTER!
    and x['pct_high'] >= 10        # POND 15% LOLOS!
    and -2 <= x['chg'] <= 15
    and 120_000_000 <= x['vol'] <= 3_000_000_000
    and x['last'] >= x['mid']*0.90
], key=lambda x: x['vol'], reverse=True)[:2]  # CUMA 2 KOIN!

akan_pairs = set([x['pair'] for x in akan])

# 2 KOIN LAGI RUNNING - DRX KE-FILTER KARENA RANGE & SISA GEDE!
lagi = sorted([
    x for x in result
    if 12 < x['pct_low'] <= 25
    and x['range_pct'] <= 45       # DRX 82% -> KE-FILTER! POND GA MASUK SINI!
    and x['pct_high'] <= 45        # DRX 53% -> KE-FILTER! JADI PUCUK!
    and x['pct_high'] >= 10
    and -2 <= x['chg'] <= 30
    and x['pair'] not in akan_pairs
], key=lambda x: x['vol'], reverse=True)[:2]  # CUMA 2 KOIN!

lagi_pairs = akan_pairs.union(set([x['pair'] for x in lagi]))

# 1 KOIN UDAH RUNNING
udah = sorted([
    x for x in result
    if 25 < x['pct_low'] <= 40
    and x['range_pct'] <= 50
    and x['pct_high'] >= 5
    and x['chg'] > -5
    and x['pair'] not in lagi_pairs
], key=lambda x: x['vol'], reverse=True)[:1]  # CUMA 1 KOIN!

# TELE PROPOR SIONAL 5 KOIN!
msg = f"V53 FINAL 5 KOIN {now} | {len(result)} scan\n\n"

if akan:
    msg += "🎯 AKAN 3-12% (2 KOIN TERBAIK):\n"
    for c in akan:
        msg += f"-> {c['pair'].upper()[:-4]} {c['pct_low']:.0f}% Vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% range {c['range_pct']:.0f}%\n"
    msg += "\n"

if lagi:
    msg += "🚀 LAGI 12-25% (2 KOIN TERBANG):\n"
    for c in lagi:
        msg += f"-> {c['pair'].upper()[:-4]} {c['pct_low']:.0f}% Vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% range {c['range_pct']:.0f}%\n"
    msg += "\n"

if udah:
    msg += "🔥 UDAH 25-40% (1 KOIN):\n"
    for c in udah:
        msg += f"-> {c['pair'].upper()[:-4]} {c['pct_low']:.0f}% sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if not akan and not lagi and not udah:
    msg += "KOSONG - MARKET OFF\n"

print(msg)
send_tele(msg)
