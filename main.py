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
        if low==0 or last<10: continue # tendang koin 11 rupiah kayak UNMD!
        if last < low*0.9 or last > high*1.1: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 45: continue # tendang koin liar 44% kayak UNMD!
        result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v):
    return f"{v/1_000_000_000:.2f}Bn" if v>=1_000_000_000 else f"{v/1_000_000:.0f}jt"

# V42 RUNNING - VOL 350jt-900jt SISA 12-35% - BIAR GA KAYAK GTC DOWNTREND & MRS SISA 3%!
running = [x for x in result if 10 <= x['pct_low'] <= 25 and 350_000_000 <= x['vol'] <= 900_000_000 and 12 <= x['pct_high'] <= 35]
running = sorted(running, key=lambda x: x['vol'], reverse=True)[:6]

# V42 CHALLENGE - VOL >1Bn SISA >10% - KHUSUS TANTANGAN! CUMA KOIN MELEDAK KAYAK ICNT!
challenge = [x for x in result if 25 < x['pct_low'] <= 55 and x['vol'] >= 1_000_000_000 and x['pct_high'] >= 10]
challenge = sorted(challenge, key=lambda x: x['vol'], reverse=True)[:4]

msg = f"V42 TANTANGAN {now} | {len(result)} coin bersih\n\n"

if running:
    msg += "🚀 RUNNING SCALP 10-25% VOL 350-900jt SISA 12%+:\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"
else:
    msg += "🚀 RUNNING: KOSONG - GA ADA YANG FRESH! LIBUR DULU MIN!\n\n"

if challenge:
    msg += "🔥 CHALLENGE 25-55% VOL >1Bn (HIGH RISK!):\n"
    for c in challenge:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - GAS 20% MODAL!\n"
else:
    msg += "🔥 CHALLENGE: KOSONG - BELUM ADA YANG MELEDAK!\n"

print(msg)
send_tele(msg)
