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

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr',
    'btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr',
    'ern_idr','show_idr'
}

tickers = get_tickers()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'):
        continue
    if pair in BLACKLIST:
        continue
    try:
        last = float(d['last'])
        low = float(d['low'])
        high = float(d['high'])
        vol = float(d.get('vol_idr', 0))
        if low == 0: continue
        if last < 20: continue
        if vol < 200_000_000: continue
        if vol > 6_000_000_000: continue
        if last < low*0.85 or last > high*1.15: continue
            
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        
        if range_pct > 70: continue
        if pct_low < 8: continue
            
        result.append({
            'pair': pair, 'last': last, 'vol': vol,
            'pct_low': pct_low, 'pct_high': pct_high
        })
    except:
        continue

def fmt_vol(v):
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.2f} Bn"
    else:
        return f"{v/1_000_000:.0f} Mn"

# V47.2 FIX FAX - PISAH AMAN & WARNING!
running_aman = [x for x in result if 8 <= x['pct_low'] <= 22 and x['pct_high'] >= 10]
running_aman = sorted(running_aman, key=lambda x: x['pct_high'], reverse=True)[:6]

running_warn = [x for x in result if 8 <= x['pct_low'] <= 22 and 2 <= x['pct_high'] < 10]
running_warn = sorted(running_warn, key=lambda x: x['vol'], reverse=True)[:6]

mid_aman = [x for x in result if 22 < x['pct_low'] <= 35 and x['pct_high'] >= 10]
mid_aman = sorted(mid_aman, key=lambda x: x['pct_high'], reverse=True)[:6]

mid_warn = [x for x in result if 22 < x['pct_low'] <= 35 and 2 <= x['pct_high'] < 10]
mid_warn = sorted(mid_warn, key=lambda x: x['vol'], reverse=True)[:6]

challenge = [x for x in result if 35 < x['pct_low'] <= 70 and x['pct_high'] >= 1]
challenge = sorted(challenge, key=lambda x: x['vol'], reverse=True)[:6]

hampir_high = [x for x in result if x['pct_low'] >= 8 and 0 <= x['pct_high'] < 2]
hampir_high = sorted(hampir_high, key=lambda x: x['pct_low'], reverse=True)[:6]

msg = f"V47.2 FIX FAX {now} | {len(result)} coin\n\n"

if running_aman:
    msg += "🌱 RUNNING 8-22% SISA >10% (AMAN BANGET - BOLEH BELI):\n"
    for c in running_aman:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if running_warn:
    msg += "⚠️ RUNNING 8-22% SISA 2-10% (DEKET HIGH - HATI2):\n"
    for c in running_warn:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - JANGAN FOMO!\n"
    msg += "\n"

if mid_aman:
    msg += "🚀 MID 22-35% SISA >10% (MASIH OKE):\n"
    for c in mid_aman:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if mid_warn:
    msg += "🔶 MID 22-35% SISA 2-10% (UDAH TINGGI):\n"
    for c in mid_warn:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if challenge:
    msg += "🔥 CHALLENGE 35-70% SISA 1%+ (HIGH RISK - SKIP!):\n"
    for c in challenge:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - SKIP!\n"
    msg += "\n"

if hampir_high:
    msg += "✅ HAMPIR HIGH SISA <2% (TP! JANGAN BELI!):\n"
    for c in hampir_high:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - TP!\n"

if not any([running_aman, running_warn, mid_aman, mid_warn, challenge, hampir_high]):
    msg += "KOSONG - MARKET SEPI! LIBUR DULU MIN!\n"

print(msg)
send_tele(msg)
