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
        try:
            chg = float(d.get('change', d.get('24h_change', 0)))
        except:
            chg = 0
        
        if low == 0 or last < 20: continue
        if vol < 100_000_000: continue
        if vol > 10_000_000_000: continue
        if last < low*0.85 or last > high*1.15: continue
        
        pct_low = (last - low)/low*100
        pct_high = (high - last)/last*100 if last>0 else 0
        range_pct = (high - low)/low*100
        mid = (high + low)/2
        
        # FILTER DASAR - BUANG SAMPAH
        if range_pct > 100: continue
        if pct_low < 3: continue
        
        result.append({
            'pair': pair, 'vol': vol, 'pct_low': pct_low, 
            'pct_high': pct_high, 'chg': chg, 
            'range_pct': range_pct, 'mid': mid, 'last': last, 'low': low
        })
    except:
        continue

def fmt_vol(v):
    return f"{v/1_000_000_000:.2f} Bn" if v >= 1_000_000_000 else f"{v/1_000_000:.0f} Mn"

# V52 - 3 KATEGORI AKAN + LAGI + UDAH RUNNING

# 1. AKAN RUNNING 3-12% = CALON STIK 49! (baru bangun, vol akumulasi, range sempit, chg kecil)
akan = sorted([
    x for x in result 
    if 3 <= x['pct_low'] <= 12 
    and 8 <= x['range_pct'] <= 30
    and x['pct_high'] >= 15
    and 0 <= x['chg'] <= 15
    and x['vol'] >= 120_000_000
    and x['vol'] <= 2_500_000_000
    and x['last'] >= x['mid']*0.90
], key=lambda x: x['vol'], reverse=True)[:10]

akan_pairs = set([x['pair'] for x in akan])

# 2. LAGI RUNNING 12-25% = BARU TERBANG! (kayak STIK 60-90 dulu)
lagi = sorted([
    x for x in result
    if 12 < x['pct_low'] <= 25
    and x['pct_high'] >= 10
    and x['chg'] >= -3  # boleh merah tipis -3%
    and x['chg'] <= 30
    and x['pair'] not in akan_pairs
], key=lambda x: x['pct_high'], reverse=True)[:7]

lagi_pairs = akan_pairs.union(set([x['pair'] for x in lagi]))

# 3. UDAH RUNNING 25-40% = UDAH TINGGI TAPI MASIH ADA SISA
udah = sorted([
    x for x in result
    if 25 < x['pct_low'] <= 40
    and x['pct_high'] >= 8
    and x['chg'] > 0
    and x['pair'] not in lagi_pairs
], key=lambda x: x['vol'], reverse=True)[:6]

udah_pairs = lagi_pairs.union(set([x['pair'] for x in udah]))

# 4. PUCUK >40% ATAU SISA TIPIS
pucuk = sorted([
    x for x in result
    if x['pair'] not in udah_pairs and (x['pct_low'] > 40 or x['pct_high'] < 8)
], key=lambda x: x['pct_low'], reverse=True)[:5]

msg = f"V52 AKAN+LAGI+UDAH {now} | {len(result)} scan\n\n"

if akan:
    msg += "🎯 AKAN RUNNING 3-12% (CALON STIK 49! VOL AKUMULASI):\n"
    for c in akan:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% Vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% chg {c['chg']:.0f}% range {c['range_pct']:.0f}%\n"
    msg += "\n"

if lagi:
    msg += "🚀 LAGI RUNNING 12-25% (BARU TERBANG):\n"
    for c in lagi:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% chg {c['chg']:.0f}%\n"
    msg += "\n"

if udah:
    msg += "🔥 UDAH RUNNING 25-40% (TINGGI TAPI MASIH ADA SISA):\n"
    for c in udah:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg += "\n"

if pucuk:
    msg += "⚠️ PUCUK >40% / SISA TIPIS (JANGAN ENTRY GEDE):\n"
    for c in pucuk:
        msg += f"-> {c['pair'].replace('_idr','').upper()} {c['pct_low']:.0f}% {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% chg {c['chg']:.0f}%\n"

if not akan and not lagi and not udah:
    msg += "KOSONG - market sepi, semua dump kayak NOVA -13% & CAST -7%\nJANGAN ENTRY DULU!\n"

print(msg)
send_tele(msg)
