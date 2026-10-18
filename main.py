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
        # MN ONLY! DARI Mn DULU BARU KE Bn - TENDANG Bn!
        if vol >= 1_000_000_000: continue  # Tendang Bn kayak ZEREBRO 6.4Bn & NEON 3.3Bn!
        if vol < 150_000_000: continue     # Tendang yang terlalu sepi <150Mn
        if low==0 or last<10: continue     # Tendang UNMD 11 rupiah!
        if last < low*0.9 or last > high*1.1: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 60: continue        # Tendang koin liar >60%
        result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v):
    return f"{v/1_000_000:.0f} Mn"

# V43 RUNNING + V44 EARLY = RUNNING MN 10-27% - MASIH AWAL, BANDAR BARU NGUMPULIN!
running = [x for x in result if 10 <= x['pct_low'] <= 27 and x['pct_high'] >= 12]
running = sorted(running, key=lambda x: x['pct_low'], reverse=True)[:8]

# V43 CHALLENGE + V44 SUPER CHALLENGE = CHALLENGE MN 27-60% - TANTANGAN KAYAK ONL 49% CUAN 16%!
challenge = [x for x in result if 27 < x['pct_low'] <= 60 and x['pct_high'] >= 5]
challenge = sorted(challenge, key=lambda x: x['pct_low'], reverse=True)[:8]

msg = f"V45 MN ONLY TANTANGAN {now} | Flow: Mn dulu baru Bn\n"
msg += f"{len(result)} coin Mn bersih (Bn ketendang)\n\n"

if running:
    msg += "🌱 RUNNING MN 10-27% (150-999 Mn) - EARLY MASIH AWAL:\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"
else:
    msg += "🌱 RUNNING MN: KOSONG!\n\n"

if challenge:
    msg += "🔥 CHALLENGE MN 27-60% (TANTANGAN KAYAK ONL!):\n"
    for c in challenge:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - GAS!\n"
else:
    msg += "🔥 CHALLENGE MN: KOSONG!\n"

print(msg)
send_tele(msg)
