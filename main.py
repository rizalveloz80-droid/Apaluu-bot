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
    'ern_idr','show_idr','hype_idr','pippin_idr','pepe_idr','sui_idr','fartcoin_idr','cake_idr','anoa_idr','ondo_idr'
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
        # V46 FIX ANTI KOIN 11!
        if low==0: continue
        if last < 100: continue  # TENDANG KOIN RECEH 11, 15, 20, 30, 50, 90!
        if vol >= 1_000_000_000: continue  # TENDANG Bn!
        if vol < 150_000_000: continue     # TENDANG <150Mn sepi!
        if last < low*0.9 or last > high*1.1: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 60: continue
        result.append({'pair':pair,'last':last,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v):
    return f"{v/1_000_000:.0f} Mn"

# RUNNING 10-27% SISA 12%+ - TANTANGAN AWAL MASIH AMAN!
running = [x for x in result if 10 <= x['pct_low'] <= 27 and x['pct_high'] >= 12]
running = sorted(running, key=lambda x: x['pct_low'], reverse=True)[:8]

# CHALLENGE 27-60% SISA 12%+ - TANTANGAN PUCUK TAPI MASIH ADA SISA!
challenge = [x for x in result if 27 < x['pct_low'] <= 60 and x['pct_high'] >= 12]
challenge = sorted(challenge, key=lambda x: x['pct_low'], reverse=True)[:8]

msg = f"V46 MN TANTANGAN {now} | Anti koin 11 | Mn dulu baru Bn\n"
msg += f"{len(result)} coin bersih (100+ rupiah, 150-999 Mn)\n\n"

if running:
    msg += "🌱 RUNNING 10-27% SISA 12%+ (EARLY):\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% hrg {c['last']:.0f}\n"
    msg += "\n"
else:
    msg += "🌱 RUNNING: KOSONG - BELUM ADA YANG FRESH!\n\n"

if challenge:
    msg += "🔥 CHALLENGE 27-60% SISA 12%+ (MENANTANG):\n"
    for c in challenge:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% hrg {c['last']:.0f}\n"
else:
    msg += "🔥 CHALLENGE: KOSONG!\n"

print(msg)
send_tele(msg)
