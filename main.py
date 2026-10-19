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
        if vol < 100_000_000: continue  # V48 turunin 100Mn biar POND masuk!
        if vol > 6_000_000_000: continue
        if last < low*0.85 or last > high*1.15: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 70 or pct_low < 8: continue
        # HITUNG SCORE BUAT SORTING 10 BEST
        score = pct_high*0.7 + (vol/1_000_000_000)*30
        result.append({'pair': pair, 'vol': vol, 'pct_low': pct_low, 'pct_high': pct_high, 'score': score})
    except:
        continue

def fmt_vol(v):
    return f"{v/1_000_000_000:.2f} Bn" if v >= 1_000_000_000 else f"{v/1_000_000:.0f} Mn"

# V48 GOLDEN - CUMA 8-15% SISA >15% - 10 BEST ONLY!
golden_best = sorted(
    [x for x in result if 8 <= x['pct_low'] <= 15 and x['pct_high'] >= 15], 
    key=lambda x: x['score'], reverse=True
)[:10]

msg = f"V48 GOLDEN 8-15% {now} | {len(result)} scan -> {len(golden_best)} BEST\n\n"

if golden_best:
    msg += "🌱 8-15% SISA >15% - 10 BEST:\n"
    for c in golden_best:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
else:
    msg += "KOSONG - ga ada yang 8-15% sisa >15%\n"
    # Fallback: kasih yang 8-15% sisa >10% biar ga kosong banget
    fallback = sorted([x for x in result if 8 <= x['pct_low'] <= 15 and x['pct_high'] >= 10], key=lambda x: x['score'], reverse=True)[:10]
    if fallback:
        msg += "\nFALLBACK 8-15% SISA >10%:\n"
        for c in fallback:
            msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"

print(msg)
send_tele(msg)
