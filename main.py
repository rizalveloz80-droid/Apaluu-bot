import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get('tickers', {})
    except: return {}

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr',
    'btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','ada_idr','bnb_idr','trx_idr',
    'ern_idr','show_idr',
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
        # MN ONLY! TENDANG YANG Bn! (<1Bn aja!)
        if vol >= 1_000_000_000: continue
        if vol < 150_000_000: continue
        if low==0 or last<10: continue
        if last < low*0.9 or last > high*1.1: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 60: continue
        result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v):
    return f"{v/1_000_000:.0f} Mn"

running = [x for x in result if 10 <= x['pct_low'] <= 27 and 12 <= x['pct_high']]
running = sorted(running, key=lambda x: x['pct_low'], reverse=True)[:8]

challenge = [x for x in result if 27 < x['pct_low'] <= 60 and x['pct_high'] >= 5]
challenge = sorted(challenge, key=lambda x: x['vol'], reverse=True)[:8]

msg = f"V43 MN ONLY {now} | {len(result)} coin Mn bersih (tanpa Bn)\n\n"

if running:
    msg += "🚀 RUNNING 10-27% MN (150-999 Mn):\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"
else:
    msg += "🚀 RUNNING MN: KOSONG!\n\n"

if challenge:
    msg += "🔥 CHALLENGE 27-60% MN (TANTANGAN KAYA ONL!):\n"
    for c in challenge:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - HIGH RISK!\n"
else:
    msg += "🔥 CHALLENGE MN: KOSONG!\n"

print(msg)
send_tele(msg)
