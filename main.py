import requests, os
from datetime import datetime, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','paxg_idr','btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr','trx_idr','ern_idr','show_idr','pepe_idr','shib_idr'}

tickers = get_tickers()
now_wib = datetime.utcnow() + timedelta(hours=7)
now = now_wib.strftime("%H:%M WIB")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    try:
        last = float(d['last']); low = float(d['low']); high = float(d['high'])
        vol = float(d.get('vol_idr', 0))
        if low == 0 or last < 20: continue
        if vol < 200_000_000 or vol > 15_000_000_000: continue  # V52: 15Bn biar ZEREBRO masuk!

        if last < low*0.85 or last > high*1.15: continue
        if last < high*0.80: continue  # V52: ANTI SN -24% JEBakan!

        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 70: continue
        if pct_low < 8 or pct_low > 60: continue
        if pct_high < 8: continue  # V47 BEST: SISA MIN 8%+ BIKIN AMAN!

        result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v): return f"{v/1_000_000_000:.2f} Bn" if v>=1_000_000_000 else f"{v/1_000_000:.0f} Mn"

# V47 BEST: SORT SISA GEDE! No 1 = sisa gede = paling aman!
running = [x for x in result if 8 <= x['pct_low'] <= 22]
running = sorted(running, key=lambda x: x['pct_high'], reverse=True)[:5]

mid = [x for x in result if 22 < x['pct_low'] <= 35]
mid = sorted(mid, key=lambda x: x['pct_high'], reverse=True)[:5]

challenge = [x for x in result if 35 < x['pct_low'] <= 60]
challenge = sorted(challenge, key=lambda x: x['pct_high'], reverse=True)[:3]

msg = f"V52 BEST V47+V51 {now} | {len(result)} coin\n\n"
if running:
    msg += "🌱 RUNNING 8-22% SISA 8%+ (AMAN):\n"
    for c in running:
        name=c['pair'].replace('_idr','').upper()
        msg+=f"-> {name} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg+="\n"
if mid:
    msg += "🚀 MID 22-35% SISA 8%+ (TANTANGAN):\n"
    for c in mid:
        name=c['pair'].replace('_idr','').upper()
        msg+=f"-> {name} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg+="\n"
if challenge:
    msg += "🔥 CHALLENGE 35-60% SISA 8%+:\n"
    for c in challenge:
        name=c['pair'].replace('_idr','').upper()
        msg+=f"-> {name} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%!\n"
msg += "\n💡 V52: V47 BEST + anti SN -24% + vol 15Bn!"

print(msg)
send_tele(msg)
