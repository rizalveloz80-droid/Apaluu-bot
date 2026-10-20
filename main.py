import requests, os
from datetime import datetime, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print("❌ TOKEN/CHAT_ID KOSONG!")
        return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"✅ SENT {r.status_code}")
    except Exception as e:
        print(f"❌ ERROR {e}")

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
now_wib = datetime.utcnow() + timedelta(hours=7)
now = now_wib.strftime("%H:%M WIB")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    try:
        last = float(d['last']); low = float(d['low']); high = float(d['high'])
        vol = float(d.get('vol_idr',0))
        if low==0: continue
        if last < 20: continue
        if vol < 200_000_000: continue
        if vol > 6_000_000_000: continue
        if last < low*0.85 or last > high*1.15: continue
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 70: continue
        if pct_low < 8: continue
        if pct_low > 60: continue
        result.append({'pair':pair,'last':last,'vol':vol,'pct_low':pct_low,'pct_high':pct_high})
    except: continue

def fmt_vol(v):
    if v>=1_000_000_000: return f"{v/1_000_000_000:.2f} Bn"
    else: return f"{v/1_000_000:.0f} Mn"

# V49 - SORT BY SISA TERGEDE! PALING AMAN DI ATAS!
running = [x for x in result if 8 <= x['pct_low'] <= 22 and x['pct_high'] >= 8]
running = sorted(running, key=lambda x: x['pct_high'], reverse=True)[:7]  # SISA GEDE DULU!

mid = [x for x in result if 22 < x['pct_low'] <= 35 and x['pct_high'] >= 8]
mid = sorted(mid, key=lambda x: x['pct_high'], reverse=True)[:7]  # SISA GEDE DULU!

challenge = [x for x in result if 35 < x['pct_low'] <= 60 and x['pct_high'] >= 5]
challenge = sorted(challenge, key=lambda x: x['pct_high'], reverse=True)[:5]  # SISA GEDE DULU!

msg = f"V49 SORT SISA {now} | {len(result)} coin\n\n"

if running:
    msg += "🌱 RUNNING 8-22% (URUT SISA GEDE = AMAN):\n"
    for i, c in enumerate(running, 1):
        msg += f"{i}. {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if mid:
    msg += "🚀 MID 22-35% (URUT SISA GEDE):\n"
    for i, c in enumerate(mid, 1):
        msg += f"{i}. {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if challenge:
    msg += "🔥 CHALLENGE 35-60% (URUT SISA GEDE):\n"
    for i, c in enumerate(challenge, 1):
        msg += f"{i}. {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% - HIGH RISK!\n"
    msg += "\n"

if not running and not mid and not challenge:
    msg += "💤 SEPI - Ga ada lolos!\n"

msg += "\n💡 No 1 = sisa paling gede = paling aman!"

print(msg)
send_tele(msg)
