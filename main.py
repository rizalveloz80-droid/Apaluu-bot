import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_tickers():
    try:
        return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','xrp_idr','sol_idr','doge_idr','bnb_idr'}

tickers = get_tickers()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M")
result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    try:
        last = float(d['last']); low = float(d['low']); high = float(d['high'])
        vol = float(d.get('vol_idr', 0)); chg = float(d.get('change', 0))
        if low==0 or last<20: continue
        if vol<100_000_000 or vol>10_000_000_000: continue
        
        pct_low = (last-low)/low*100
        pct_high = (high-last)/last*100  # SISA = JARAK KE RESISTANCE!
        range_pct = (high-low)/low*100   # RANGE = SEBERAPA GEDE PUMP HARI INI!
        mid = (high+low)/2
        
        if range_pct>100 or pct_low<3: continue
        result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high,'chg':chg,'range_pct':range_pct,'mid':mid,'last':last,'high':high})
    except: continue

def fmt_vol(v):
    return f"{v/1e9:.2f} Bn" if v>=1e9 else f"{v/1e6:.0f} Mn"

# ===== V54 FINAL LOCK FOREVER - FILTER RESISTANCE + SEMUA PELAJARAN! =====
# RULE FINAL GA GANTI LAGI!

# 1. POND LESSON: mid*0.90 jangan 0.98!
# 2. DRX LESSON: range <=45 & sisa <=45! range 82% = PUCUK!
# 3. ANOA LESSON: chg >=0! chg -1,43% = LAGI DUMP!
# 4. RESISTANCE LESSON: sisa >=15%! sisa 11% = UDAH DI RESISTANCE 217!

akan = sorted([
    x for x in result 
    if 3 <= x['pct_low'] <= 12              # Calon STIK 49
    and 8 <= x['range_pct'] <= 35           # FIX RESISTANCE! Max 35%! ANOA 15% lolos, DRX 82% HILANG!
    and 15 <= x['pct_high'] <= 40           # FIX RESISTANCE! Minimal 15% dari High! Punya ruang naik! ANOA 11% HILANG! POND 15% LOLOS!
    and 0 <= x['chg'] <= 15                 # FIX ANOA! Chg negatif = dump = buang!
    and 120_000_000 <= x['vol'] <= 2_500_000_000
    and x['last'] >= x['mid']*0.90          # POND LESSON! 0.90!
    and x['last'] < x['high']*0.92          # FIX RESISTANCE BARU! Harus di bawah 92% High! Kalo >92% High = udah di resistance!
], key=lambda x: x['pct_high'], reverse=True)[:2]

akan_pairs = set([x['pair'] for x in akan])

lagi = sorted([
    x for x in result
    if 12 < x['pct_low'] <= 25
    and x['range_pct'] <= 40                # FIX DRX! Range gede = udah pump!
    and 12 <= x['pct_high'] <= 40          # FIX RESISTANCE! Sisa jangan kegedean (high basi) & jangan kekecilan (udah di resistance)
    and 0 <= x['chg'] <= 25
    and x['pair'] not in akan_pairs
    and x['last'] < x['high']*0.93
], key=lambda x: x['vol'], reverse=True)[:2]

lagi_pairs = akan_pairs.union(set([x['pair'] for x in lagi]))

udah = sorted([
    x for x in result
    if 25 < x['pct_low'] <= 38
    and x['range_pct'] <= 45
    and 5 <= x['pct_high'] <= 35
    and x['chg'] >= 0
    and x['pair'] not in lagi_pairs
], key=lambda x: x['vol'], reverse=True)[:1]

msg = f"V54 FINAL RESISTANCE {now} | {len(result)} scan\n\n"

if akan:
    msg += "🎯 AKAN 3-12% (2 KOIN - ADA RUANG 15% KE RESISTANCE):\n"
    for c in akan:
        msg += f"-> {c['pair'].upper()[:-4]} {c['pct_low']:.0f}% Vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% range {c['range_pct']:.0f}% chg {c['chg']:.0f}%\n"
    msg += "\n"

if lagi:
    msg += "🚀 LAGI 12-25% (2 KOIN):\n"
    for c in lagi:
        msg += f"-> {c['pair'].upper()[:-4]} {c['pct_low']:.0f}% Vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}% range {c['range_pct']:.0f}%\n"
    msg += "\n"

if udah:
    msg += "🔥 UDAH 25-38% (1 KOIN):\n"
    for c in udah:
        msg += f"-> {c['pair'].upper()[:-4]} {c['pct_low']:.0f}% sisa {c['pct_high']:.0f}%\n"

if not akan and not lagi and not udah:
    msg += "KOSONG - SEMUA DI RESISTANCE / PUCUK - JANGAN ENTRY!\n"

print(msg)
send_tele(msg)
