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

# BLACKLIST V17-V25 - LEBIH SEDIKIT! GA TERLALU BANYAK TENDANG!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr',
    'btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr',
    'ern_idr','show_idr'
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
        # V17-V25 STYLE - LONGGAR TAPI MASIH AMAN!
        if low==0: continue
        if last < 20: continue  # V17 dulu 20, bukan 100! Jadi UNMD 11 ketendang, tapi 25 masih masuk!
        if vol < 200_000_000: continue  # V20 dulu 200Mn minimal
        if vol > 6_000_000_000: continue  # Tendang yang udah 6Bn+ aja kayak ZEREBRO
        if last < low*0.85 or last > high*1.15: continue  # Lebih longgar
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 70: continue  # V25 dulu 70%, bukan 60%
        if pct_low < 8: continue  # Minimal 8% kayak V17
        result.append({'pair':pair,'last':last,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v):
    if v>=1_000_000_000: return f"{v/1_000_000_000:.2f} Bn"
    else: return f"{v/1_000_000:.0f} Mn"

# V17-V25 BEST TIER - 3 KATEGORI!
# RUNNING V21 - 8-22% SISA 8%+ (LONGGAR!)
running = [x for x in result if 8 <= x['pct_low'] <= 22 and x['pct_high'] >= 8]
running = sorted(running, key=lambda x: x['vol'], reverse=True)[:6]

# MID V23 - 22-35% SISA 8%+ (TANTANGAN MENENGAH KAYAK GTC!)
mid = [x for x in result if 22 < x['pct_low'] <= 35 and x['pct_high'] >= 8]
mid = sorted(mid, key=lambda x: x['pct_low'], reverse=True)[:6]

# CHALLENGE V25 - 35-55% SISA 5%+ (SUPER TANTANGAN KAYAK ONL & ICNT!)
challenge = [x for x in result if 35 < x['pct_low'] <= 60 and x['pct_high'] >= 5]
challenge = sorted(challenge, key=lambda x: x['vol'], reverse=True)[:6]

msg = f"V47 BEST V17-V25 {now} | {len(result)} coin\n\n"

if running:
    msg += "🌱 RUNNING 8-22% SISA 8%+ (AMAN):\n"
    for c in running:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if mid:
    msg += "🚀 MID 22-35% SISA 8%+ (TANTANGAN):\n"
    for c in mid:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if challenge:
    msg += "🔥 CHALLENGE 35-60% SISA 5%+ (SUPER TANTANGAN):\n"
    for c in challenge:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - HIGH RISK!\n"

if not running and not mid and not challenge:
    msg += "KOSONG - MARKET SEPI! LIBUR DULU MIN!\n"

print(msg)
send_tele(msg)
