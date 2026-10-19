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
        print(f"✅ TELE SENT {r.status_code}")
    except Exception as e:
        print(f"❌ TELE ERROR {e}")

def get_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get('tickers', {})
    except:
        return {}

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','paxg_idr',
    'btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr','trx_idr',
    'ern_idr','show_idr','pepe_idr','shib_idr'
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
        vol = float(d.get('vol_idr', 0))
        if low == 0: continue
        if last < 20: continue
        if vol < 200_000_000: continue
        if vol > 15_000_000_000: continue  # V51 - 15 Bn biar ZEREBRO masuk

        # === V51 FIX ANTI JEBAKAN SN -24% ===
        if last < low*0.85 or last > high*1.15: continue
        if last < high*0.75: continue  # Kalo dump 25% dari high kayak SN, SKIP!
        # Kalo ada field change, filter -10%
        try:
            ch = float(d.get('change', 0))
            if ch < -10: continue
        except:
            pass
        # === END FIX ===

        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        if range_pct > 70: continue
        if pct_low < 8: continue
        if pct_low > 60: continue
        result.append({
            'pair': pair,
            'last': last,
            'vol': vol,
            'pct_low': pct_low,
            'pct_high': pct_high
        })
    except:
        continue

def fmt_vol(v):
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.2f} Bn"
    else:
        return f"{v/1_000_000:.0f} Mn"

# V51 SORT SISA TERGEDE = PALING AMAN DI ATAS!
running = [x for x in result if 8 <= x['pct_low'] <= 22 and x['pct_high'] >= 5]
running = sorted(running, key=lambda x: x['pct_high'], reverse=True)[:7]

mid = [x for x in result if 22 < x['pct_low'] <= 35 and x['pct_high'] >= 5]
mid = sorted(mid, key=lambda x: x['pct_high'], reverse=True)[:7]

challenge = [x for x in result if 35 < x['pct_low'] <= 60 and x['pct_high'] >= 3]
challenge = sorted(challenge, key=lambda x: x['pct_high'], reverse=True)[:5]

msg = f"V51 ANTI-DUMP {now} | {len(result)} coin\n\n"

if running:
    msg += "🌱 RUNNING 8-22% (No 1 = sisa gede = aman):\n"
    for i, c in enumerate(running, 1):
        name = c['pair'].replace('_idr','').upper()
        msg += f"{i}. {name} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if mid:
    msg += "🚀 MID 22-35% (No 1 = sisa gede):\n"
    for i, c in enumerate(mid, 1):
        name = c['pair'].replace('_idr','').upper()
        msg += f"{i}. {name} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if challenge:
    msg += "🔥 CHALLENGE 35-60%:\n"
    for i, c in enumerate(challenge, 1):
        name = c['pair'].replace('_idr','').upper()
        msg += f"{i}. {name} {c['pct_low']:.0f}% low {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%!\n"
    msg += "\n"

if not running and not mid and not challenge:
    msg += "💤 SEPI - Ga ada yang lolos!\n"

msg += "💡 V51: SN -24% auto ke-filter! No 1 = aman!"

print(msg)
send_tele(msg)
