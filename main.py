import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except:
        pass

def get_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get('tickers', {})
    except:
        return {}

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr','ern_idr','show_idr'}

tickers = get_tickers()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    try:
        last = float(d['last']); low = float(d['low']); high = float(d['high']); vol = float(d.get('vol_idr', 0))
        if low == 0 or last < 20: continue
        if vol < 100_000_000: continue
        if vol > 15_000_000_000: continue
        if last < low*0.85 or last > high*1.15: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 120 or pct_low < 8: continue
        result.append({'pair': pair, 'vol': vol, 'pct_low': pct_low, 'pct_high': pct_high})
    except:
        continue

def fmt_vol(v):
    return f"{v/1_000_000_000:.2f} Bn" if v >= 1_000_000_000 else f"{v/1_000_000:.0f} Mn"

# V50 - RESISTANCE LOGIC!
# Lu mau running yang belum ketinggalan = sisa gede!
running = sorted([x for x in result if 10 <= x['pct_low'] <= 25 and 150_000_000 <= x['vol'] <= 800_000_000 and x['pct_high'] >= 15], key=lambda x: x['pct_high'], reverse=True)[:5]
golden = sorted([x for x in result if 8 <= x['pct_low'] <= 16 and x['pct_high'] >= 10], key=lambda x: x['pct_high'], reverse=True)[:6]
trending_ok = sorted([x for x in result if 16 < x['pct_low'] <= 35 and x['pct_high'] >= 10], key=lambda x: x['vol'], reverse=True)[:5]
pucuk = sorted([x for x in result if x['pct_low'] > 35], key=lambda x: x['pct_low'], reverse=True)[:5]

msg = f"V50 RESISTANCE {now} | {len(result)} scan\n\n"

if running:
    msg += "🚀 RUNNING 10-25% VOL KECIL (150-800jt) SISA >15%:\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% Vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if golden:
    msg += "🌱 GOLDEN 8-16% SISA >10%:\n"
    for c in golden:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if trending_ok:
    msg += "🔥 TRENDING 16-35% SISA >10% (masih ada resistance):\n"
    for c in trending_ok:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if pucuk:
    msg += "⚠️ PUCUK >35% JANGAN ENTRY (udah mentok):\n"
    for c in pucuk:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"

if not running and not golden and not trending_ok:
    msg += "KOSONG - semua udah pucuk / sisa tipis\n"

print(msg)
send_tele(msg)
