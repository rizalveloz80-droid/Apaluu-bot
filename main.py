import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v73_rotation.json" # GANTI FILE BARU BIAR FRESH!

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg},timeout=15)
    except: pass
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE,'r') as f: return json.load(f)
        except: return {}
    return {}
def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)
def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}
def fnum(v,d=0.0):
    try:
        v=str(v).replace(',','').strip()
        return float(v) if v else d
    except: return d

# BLACKLIST TETAP DI BLOCK PERMANEN!
BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','ern_idr','luna_idr','lunc_idr','ftt_idr','bsv_idr','bcha_idr'}

state=load_state()
now_ts=time.time()
tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M")
result=[]

for pair,d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    # YANG DIBLOCK MANUAL TETAP DI BLOCK!
    if state.get(pair,{}).get('blocked_permanent'): continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high'))
    vol=fnum(d.get('vol_idr')); chg=fnum(d.get('change'))
    if low<=0 or last<30: continue
    if vol<50_000_000 or vol>10_000_000_000: continue # TURUNIN KE 50Mn BIAR KOIN MAU PUMP KEDETECT!
    pct_low=(last-low)/low*100 if low>0 else 0
    range_pct=(high-low)/low*100 if low>0 else 0
    pct_from_high=(high-last)/high*100 if high>0 else 0

    # === FILTER SAFE - YANG MINUS TETAP KE BLOCK! ===
    if not (0.2 <= pct_low <= 1.8):
        if chg < 0.5: continue # GTC -3% PM -5% ZORA -4% PHA -6% = TETAP BLOCK!

    if pct_from_high > 10 and pct_low > 10: continue
    if pct_from_high > 8 and pct_low > 15: continue
    if last >= high*0.96: continue

    result.append({'pair':pair,'last':last,'low':low,'high':high,'vol':vol,'chg':chg,'pct_low':pct_low,'range_pct':range_pct,'pct_from_high':pct_from_high})

def fmt_vol(v): return f"{v/1e9:.2f} Bn" if v>=1e9 else f"{v/1e6:.0f} Mn"
def boleh(pair, cd):
    s=state.get(pair,{}); return now_ts - s.get('time',0) >= cd*60
def vol_growth(pair, curr_vol):
    s=state.get(pair,{})
    prev=s.get('vol',curr_vol)
    if prev<=0: return 1.0
    return curr_vol/prev

akum=[]; pemula=[]; akan=[]; lagi=[]; trending=[]

# AKUM 0.2-1.8% - ROTATION! Kalo udah 3x muncul block 2 jam!
for x in result:
    s=state.get(x['pair'],{})
    # YANG UDAH 3x MUNCUL = BLOCK 2 JAM BIAR KOIN LAIN MASUK!
    if s.get('count',0)>=3 and now_ts - s.get('time',0) < 7200:
        continue # SKYAI USELESS kalo udah 3x, tetap di block 2 jam!
    growth=vol_growth(x['pair'], x['vol'])
    if not (0.2 <= x['pct_low'] <= 1.8 and (x['vol']>=50_000_000 or growth>=1.5)): continue
    if not boleh(x['pair'],10): continue
    akum.append(x)

# PEMULA 1.8-8% - DETEKSI VOL NAIK 1.8x = MAU PUMP!
for x in result:
    if x['pair'] in {y['pair'] for y in akum}: continue
    s=state.get(x['pair'],{})
    if s.get('count',0)>=3 and now_ts - s.get('time',0) < 7200: continue
    growth=vol_growth(x['pair'], x['vol'])
    if not (1.8 <= x['pct_low'] <= 8 and x['range_pct']<=60 and (x['vol']>=80_000_000 or growth>=1.8) and x['chg']>=0.2): continue
    if not boleh(x['pair'],15): continue
    pemula.append(x)

# AKAN 8-20% - VOL GROWTH 2x = BARU MAU RUNNING!
for x in result:
    if x['pair'] in {y['pair'] for y in akum+pemula}: continue
    s=state.get(x['pair'],{})
    if s.get('count',0)>=3 and now_ts - s.get('time',0) < 7200: continue
    growth=vol_growth(x['pair'], x['vol'])
    if growth >= 2.0:
        if not (5 < x['pct_low'] <= 20): continue
    else:
        if not (8 < x['pct_low'] <= 20 and x['chg']>=1 and x['pct_from_high']<=8): continue
    if not boleh(x['pair'],15): continue
    akan.append(x)

# LAGI 20-40%
for x in result:
    if x['pair'] in {y['pair'] for y in akum+pemula+akan}: continue
    s=state.get(x['pair'],{})
    if s.get('count',0)>=3 and now_ts - s.get('time',0) < 7200: continue
    if not (20 < x['pct_low'] <= 40 and x['vol']>=200_000_000 and x['chg']>=3 and x['pct_from_high']<=8): continue
    if not boleh(x['pair'],15): continue
    lagi.append(x)

# TRENDING
for x in result:
    if x['pair'] in {y['pair'] for y in akum+pemula+akan+lagi}: continue
    s=state.get(x['pair'],{})
    if s.get('count',0)>=3 and now_ts - s.get('time',0) < 7200: continue
    if not ((x['chg']>=10 and x['vol']>=200_000_000 and x['pct_from_high']<=7) or (x['pct_low']>=35 and x['chg']>=5 and x['pct_from_high']<=7)): continue
    if not boleh(x['pair'],10): continue
    trending.append(x)

# SIMPAN STATE + COUNT! YANG DI BLOCK TETAP DI BLOCK!
for x in akum+pemula+akan+lagi+trending:
    prev=state.get(x['pair'],{})
    state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts,'count':prev.get('count',0)+1,'blocked_permanent':prev.get('blocked_permanent',False)}
save_state(state)

msg=f"SCAN V7.3 ROTATION {now} WIB | {len(result)} koin\n\n"
if trending:
    msg+="🔥 TRENDING:\n"
    for c in trending: msg+=f"-> {c['pair'].upper()[:-4]} CHG {c['chg']:.1f}% naik {c['pct_low']:.0f}% vol {fmt_vol(c['vol'])}\n"
    msg+="\n"
if lagi:
    msg+="🚀 LAGI 20-40%:\n"
    for c in lagi: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% CHG {c['chg']:.1f}% vol {fmt_vol(c['vol'])}\n"
    msg+="\n"
if akan:
    msg+="🎯 AKAN 8-20% (MAU RUNNING!):\n"
    for c in akan: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% CHG {c['chg']:.1f}% vol {fmt_vol(c['vol'])} growth {vol_growth(c['pair'], c['vol']):.1f}x\n"
    msg+="\n"
if pemula:
    msg+="🌱 PEMULA 1.8-8% (BARU MAU!):\n"
    for c in pemula: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% CHG {c['chg']:.1f}% vol {fmt_vol(c['vol'])}\n"
    msg+="\n"
if akum:
    msg+="💎 AKUM 0.2-1.8%:\n"
    for c in akum: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% vol {fmt_vol(c['vol'])}\n"

if not (trending or lagi or akan or pemula or akum):
    print(f"V7.3 {now} | {len(result)} koin | Sepi, SKYAI USELESS lagi di block 2 jam, nunggu koin lain"); exit()

print(msg)
send_tele(msg)
